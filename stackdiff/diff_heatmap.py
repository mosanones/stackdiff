"""Heatmap module: ranks keys by change frequency across multiple DiffResults."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import List, Sequence

from stackdiff.diff_engine import DiffResult


@dataclass
class HeatmapEntry:
    key: str
    change_count: int
    frequency: float  # 0.0 – 1.0 relative to total diffs supplied

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "change_count": self.change_count,
            "frequency": round(self.frequency, 4),
        }


@dataclass
class DiffHeatmap:
    total_diffs: int
    entries: List[HeatmapEntry] = field(default_factory=list)

    # entries sorted hottest-first
    @property
    def hottest(self) -> List[HeatmapEntry]:
        return sorted(self.entries, key=lambda e: e.change_count, reverse=True)

    def as_dict(self) -> dict:
        return {
            "total_diffs": self.total_diffs,
            "entries": [e.as_dict() for e in self.hottest],
        }


def build_heatmap(diffs: Sequence[DiffResult]) -> DiffHeatmap:
    """Count how often each key changes across *diffs* and return a heatmap."""
    total = len(diffs)
    counter: Counter[str] = Counter()

    for dr in diffs:
        changed_keys = set(dr.removed) | set(dr.added) | set(dr.changed)
        counter.update(changed_keys)

    entries = [
        HeatmapEntry(
            key=key,
            change_count=count,
            frequency=count / total if total else 0.0,
        )
        for key, count in counter.items()
    ]

    return DiffHeatmap(total_diffs=total, entries=entries)
