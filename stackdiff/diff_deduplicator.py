"""Deduplicates repeated diff results across multiple runs, identifying keys
that have been consistently changed versus transient/flapping changes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from stackdiff.diff_engine import DiffResult


@dataclass
class DeduplicatedKey:
    key: str
    occurrences: int
    total_runs: int
    last_removed: Optional[str]
    last_added: Optional[str]

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "occurrences": self.occurrences,
            "total_runs": self.total_runs,
            "frequency": round(self.occurrences / self.total_runs, 3) if self.total_runs else 0.0,
            "last_removed": self.last_removed,
            "last_added": self.last_added,
        }

    @property
    def is_stable(self) -> bool:
        """True when the key changed in every observed run."""
        return self.occurrences == self.total_runs

    @property
    def is_flapping(self) -> bool:
        """True when the key changed in fewer than half the runs."""
        if self.total_runs == 0:
            return False
        return (self.occurrences / self.total_runs) < 0.5


@dataclass
class DeduplicatedDiff:
    total_runs: int
    keys: List[DeduplicatedKey] = field(default_factory=list)

    def stable_keys(self) -> List[DeduplicatedKey]:
        return [k for k in self.keys if k.is_stable]

    def flapping_keys(self) -> List[DeduplicatedKey]:
        return [k for k in self.keys if k.is_flapping]

    def as_dict(self) -> dict:
        return {
            "total_runs": self.total_runs,
            "unique_changed_keys": len(self.keys),
            "stable_keys": len(self.stable_keys()),
            "flapping_keys": len(self.flapping_keys()),
            "keys": [k.as_dict() for k in self.keys],
        }


def deduplicate_diffs(results: List[DiffResult]) -> DeduplicatedDiff:
    """Aggregate multiple DiffResult objects and compute per-key change frequency."""
    total_runs = len(results)
    counts: Dict[str, int] = {}
    last_removed: Dict[str, Optional[str]] = {}
    last_added: Dict[str, Optional[str]] = {}

    for result in results:
        seen_in_run: set = set()
        for key, value in (result.removed or {}).items():
            seen_in_run.add(key)
            last_removed[key] = value
        for key, value in (result.added or {}).items():
            seen_in_run.add(key)
            last_added[key] = value
        for key in seen_in_run:
            counts[key] = counts.get(key, 0) + 1

    keys = [
        DeduplicatedKey(
            key=key,
            occurrences=count,
            total_runs=total_runs,
            last_removed=last_removed.get(key),
            last_added=last_added.get(key),
        )
        for key, count in sorted(counts.items(), key=lambda x: -x[1])
    ]

    return DeduplicatedDiff(total_runs=total_runs, keys=keys)
