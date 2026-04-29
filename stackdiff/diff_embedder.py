"""diff_embedder.py – generate a compact fingerprint vector from a DiffResult.

The vector can be used for similarity search, clustering, or anomaly detection.
Each dimension corresponds to a normalised feature of the diff.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List

from stackdiff.diff_engine import DiffResult
from stackdiff.annotator import AnnotatedDiff, annotate_diff
from stackdiff.scorer import score_annotated


@dataclass
class DiffVector:
    """A fixed-length numeric representation of a diff."""

    label_a: str
    label_b: str
    dimensions: List[float] = field(default_factory=list)

    # ------------------------------------------------------------------ #
    # dimension names (same order as `dimensions`)
    # ------------------------------------------------------------------ #
    DIMENSION_NAMES: List[str] = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "DIMENSION_NAMES",
            [
                "total_changes",
                "added_ratio",
                "removed_ratio",
                "changed_ratio",
                "critical_ratio",
                "high_ratio",
                "score_normalised",
                "log_total",
            ],
        )

    def as_dict(self) -> dict:
        return {
            "label_a": self.label_a,
            "label_b": self.label_b,
            "dimensions": dict(zip(self.DIMENSION_NAMES, self.dimensions)),
        }

    def magnitude(self) -> float:
        """Euclidean length of the vector."""
        return math.sqrt(sum(x * x for x in self.dimensions))

    def cosine_similarity(self, other: "DiffVector") -> float:
        """Cosine similarity in [−1, 1] (returns 0.0 if either vector is zero)."""
        mag = self.magnitude() * other.magnitude()
        if mag == 0.0:
            return 0.0
        dot = sum(a * b for a, b in zip(self.dimensions, other.dimensions))
        return dot / mag


def embed_diff(result: DiffResult) -> DiffVector:
    """Compute a DiffVector from a DiffResult."""
    annotated: AnnotatedDiff = annotate_diff(result)
    score_obj = score_annotated(annotated)

    total = len(result.added) + len(result.removed) + len(result.changed)
    _safe = max(total, 1)

    added_ratio = len(result.added) / _safe
    removed_ratio = len(result.removed) / _safe
    changed_ratio = len(result.changed) / _safe

    annotations = annotated.annotations
    _ann_total = max(len(annotations), 1)
    critical_ratio = sum(1 for a in annotations if a.severity == "critical") / _ann_total
    high_ratio = sum(1 for a in annotations if a.severity == "high") / _ann_total

    score_normalised = min(score_obj.score / 100.0, 1.0)
    log_total = math.log1p(total)

    dimensions = [
        float(total),
        added_ratio,
        removed_ratio,
        changed_ratio,
        critical_ratio,
        high_ratio,
        score_normalised,
        log_total,
    ]

    return DiffVector(
        label_a=result.label_a,
        label_b=result.label_b,
        dimensions=dimensions,
    )
