"""diff_rollup.py — aggregate multiple DiffResults into a rollup summary."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any

from stackdiff.diff_engine import DiffResult


@dataclass
class RollupEntry:
    label: str
    added: int
    removed: int
    changed: int
    total: int

    def as_dict(self) -> Dict[str, Any]:
        return {
            "label": self.label,
            "added": self.added,
            "removed": self.removed,
            "changed": self.changed,
            "total": self.total,
        }


@dataclass
class RollupReport:
    entries: List[RollupEntry] = field(default_factory=list)

    @property
    def total_changes(self) -> int:
        return sum(e.total for e in self.entries)

    @property
    def most_changed(self) -> RollupEntry | None:
        if not self.entries:
            return None
        return max(self.entries, key=lambda e: e.total)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "entries": [e.as_dict() for e in self.entries],
            "total_changes": self.total_changes,
            "most_changed": self.most_changed.label if self.most_changed else None,
        }


def _count_changes(result: DiffResult) -> Dict[str, int]:
    added = sum(1 for v in result.added.values() if v is not None)
    removed = sum(1 for v in result.removed.values() if v is not None)
    changed = len(result.changed)
    return {"added": len(result.added), "removed": len(result.removed), "changed": changed}


def build_rollup(labeled_results: List[tuple[str, DiffResult]]) -> RollupReport:
    """Build a RollupReport from a list of (label, DiffResult) pairs."""
    entries: List[RollupEntry] = []
    for label, result in labeled_results:
        counts = _count_changes(result)
        total = counts["added"] + counts["removed"] + counts["changed"]
        entries.append(
            RollupEntry(
                label=label,
                added=counts["added"],
                removed=counts["removed"],
                changed=counts["changed"],
                total=total,
            )
        )
    return RollupReport(entries=entries)
