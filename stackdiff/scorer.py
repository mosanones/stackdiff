"""Score a diff result by severity and change volume."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from stackdiff.diff_engine import DiffResult
from stackdiff.annotator import AnnotatedDiff, Severity

SEVERITY_WEIGHTS = {
    Severity.CRITICAL: 10,
    Severity.HIGH: 5,
    Severity.MEDIUM: 2,
    Severity.LOW: 1,
}


@dataclass
class DiffScore:
    total: int
    critical: int
    high: int
    medium: int
    low: int
    label: str

    def as_dict(self) -> dict:
        return {
            "total": self.total,
            "critical": self.critical,
            "high": self.high,
            "medium": self.medium,
            "low": self.low,
            "label": self.label,
        }


def _label(total: int) -> str:
    if total == 0:
        return "clean"
    if total < 10:
        return "low-risk"
    if total < 30:
        return "moderate"
    return "high-risk"


def score_annotated(annotated: AnnotatedDiff) -> DiffScore:
    counts = {s: 0 for s in Severity}
    for ann in annotated.annotations:
        counts[ann.severity] += 1
    total = sum(SEVERITY_WEIGHTS[s] * counts[s] for s in Severity)
    return DiffScore(
        total=total,
        critical=counts[Severity.CRITICAL],
        high=counts[Severity.HIGH],
        medium=counts[Severity.MEDIUM],
        low=counts[Severity.LOW],
        label=_label(total),
    )


def score_diff(diff: DiffResult) -> DiffScore:
    """Lightweight scoring without annotations (change count only)."""
    n = len(diff.removed) + len(diff.added) + len(diff.changed)
    total = n * SEVERITY_WEIGHTS[Severity.LOW]
    return DiffScore(
        total=total,
        critical=0,
        high=0,
        medium=0,
        low=n,
        label=_label(total),
    )
