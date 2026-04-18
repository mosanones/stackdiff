"""Compute numeric statistics from a DiffResult."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict
from stackdiff.diff_engine import DiffResult


@dataclass
class DiffStats:
    total_keys: int = 0
    added: int = 0
    removed: int = 0
    changed: int = 0
    unchanged: int = 0
    change_rate: float = 0.0
    key_counts: Dict[str, int] = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "total_keys": self.total_keys,
            "added": self.added,
            "removed": self.removed,
            "changed": self.changed,
            "unchanged": self.unchanged,
            "change_rate": round(self.change_rate, 4),
        }


def compute_stats(result: DiffResult) -> DiffStats:
    """Derive counts and rates from a DiffResult."""
    added = len(result.added)
    removed = len(result.removed)
    changed = len(result.changed)

    all_keys = (
        set(result.added)
        | set(result.removed)
        | set(result.changed)
        | set(result.unchanged)
    )
    total = len(all_keys)
    unchanged = len(result.unchanged)
    change_rate = (added + removed + changed) / total if total else 0.0

    return DiffStats(
        total_keys=total,
        added=added,
        removed=removed,
        changed=changed,
        unchanged=unchanged,
        change_rate=change_rate,
        key_counts={
            "added": added,
            "removed": removed,
            "changed": changed,
            "unchanged": unchanged,
        },
    )
