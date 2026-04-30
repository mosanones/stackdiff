"""Drift detection: identify keys that have changed across multiple diff runs over time."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from stackdiff.diff_engine import DiffResult


@dataclass
class DriftEntry:
    key: str
    change_count: int
    first_seen: str
    last_seen: str
    current_removed: Optional[str]
    current_added: Optional[str]

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "change_count": self.change_count,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "current_removed": self.current_removed,
            "current_added": self.current_added,
        }


@dataclass
class DriftReport:
    entries: List[DriftEntry] = field(default_factory=list)
    total_runs: int = 0

    @property
    def drifting_keys(self) -> List[str]:
        """Keys that changed in more than one run."""
        return [e.key for e in self.entries if e.change_count > 1]

    @property
    def stable_changed_keys(self) -> List[str]:
        """Keys that changed in exactly one run."""
        return [e.key for e in self.entries if e.change_count == 1]

    def as_dict(self) -> dict:
        return {
            "total_runs": self.total_runs,
            "drifting_keys": self.drifting_keys,
            "stable_changed_keys": self.stable_changed_keys,
            "entries": [e.as_dict() for e in self.entries],
        }


def detect_drift(history: List[Dict]) -> DriftReport:
    """Detect drift from a list of history entries (as produced by diff_history).

    Each entry is expected to have:
      - 'timestamp': ISO string
      - 'removed': dict of key -> old_value
      - 'added': dict of key -> new_value
    """
    key_counts: Dict[str, int] = {}
    key_first: Dict[str, str] = {}
    key_last: Dict[str, str] = {}
    key_removed: Dict[str, Optional[str]] = {}
    key_added: Dict[str, Optional[str]] = {}

    for entry in history:
        ts = entry.get("timestamp", "")
        removed = entry.get("removed", {})
        added = entry.get("added", {})
        all_keys = set(removed) | set(added)
        for k in all_keys:
            key_counts[k] = key_counts.get(k, 0) + 1
            if k not in key_first:
                key_first[k] = ts
            key_last[k] = ts
            key_removed[k] = removed.get(k)
            key_added[k] = added.get(k)

    entries = [
        DriftEntry(
            key=k,
            change_count=key_counts[k],
            first_seen=key_first[k],
            last_seen=key_last[k],
            current_removed=key_removed.get(k),
            current_added=key_added.get(k),
        )
        for k in sorted(key_counts)
    ]
    return DriftReport(entries=entries, total_runs=len(history))
