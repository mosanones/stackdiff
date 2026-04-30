"""Detect outlier keys across multiple diff results.

An outlier key is one that changed in only a minority of the provided
diff results, suggesting an anomalous or environment-specific change.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from stackdiff.diff_engine import DiffResult


@dataclass
class OutlierEntry:
    key: str
    change_count: int
    total_diffs: int
    frequency: float  # 0.0 – 1.0
    sample_removed: Optional[str]
    sample_added: Optional[str]

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "change_count": self.change_count,
            "total_diffs": self.total_diffs,
            "frequency": round(self.frequency, 4),
            "sample_removed": self.sample_removed,
            "sample_added": self.sample_added,
        }


@dataclass
class DiffOutliers:
    total_diffs: int
    threshold: float
    outliers: List[OutlierEntry] = field(default_factory=list)

    def top(self, n: int = 5) -> List[OutlierEntry]:
        return sorted(self.outliers, key=lambda e: e.frequency)[:n]

    def as_dict(self) -> dict:
        return {
            "total_diffs": self.total_diffs,
            "threshold": self.threshold,
            "outliers": [e.as_dict() for e in self.outliers],
        }


def detect_outliers(
    diffs: List[DiffResult],
    threshold: float = 0.5,
) -> DiffOutliers:
    """Return keys that changed in fewer than *threshold* fraction of diffs.

    Args:
        diffs: List of DiffResult objects to analyse.
        threshold: Keys with frequency < threshold are considered outliers.
                   Defaults to 0.5 (changed in fewer than half the diffs).
    """
    if not diffs:
        return DiffOutliers(total_diffs=0, threshold=threshold)

    total = len(diffs)
    key_counts: Dict[str, int] = {}
    key_samples: Dict[str, tuple] = {}

    for dr in diffs:
        changed_keys = set(dr.removed) | set(dr.added) | set(dr.changed)
        for key in changed_keys:
            key_counts[key] = key_counts.get(key, 0) + 1
            if key not in key_samples:
                removed_val = dr.removed.get(key) or (dr.changed.get(key) or [None, None])[0]
                added_val = dr.added.get(key) or (dr.changed.get(key) or [None, None])[-1]
                key_samples[key] = (
                    str(removed_val) if removed_val is not None else None,
                    str(added_val) if added_val is not None else None,
                )

    outliers = []
    for key, count in key_counts.items():
        freq = count / total
        if freq < threshold:
            sample = key_samples.get(key, (None, None))
            outliers.append(
                OutlierEntry(
                    key=key,
                    change_count=count,
                    total_diffs=total,
                    frequency=freq,
                    sample_removed=sample[0],
                    sample_added=sample[1],
                )
            )

    outliers.sort(key=lambda e: (e.frequency, e.key))
    return DiffOutliers(total_diffs=total, threshold=threshold, outliers=outliers)
