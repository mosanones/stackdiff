"""Summarize a DiffScore + AnnotatedDiff into a human-readable digest."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from stackdiff.annotator import AnnotatedDiff
from stackdiff.scorer import DiffScore


@dataclass
class DiffSummary:
    score: DiffScore
    annotated: AnnotatedDiff

    @property
    def total_changes(self) -> int:
        return (
            len(self.annotated.diff_result.removed)
            + len(self.annotated.diff_result.added)
            + len(self.annotated.diff_result.changed)
        )

    def critical_keys(self) -> List[str]:
        return [
            a.key for a in self.annotated.annotations if a.severity == "critical"
        ]

    def high_keys(self) -> List[str]:
        return [a.key for a in self.annotated.annotations if a.severity == "high"]


def build_summary(score: DiffScore, annotated: AnnotatedDiff) -> DiffSummary:
    return DiffSummary(score=score, annotated=annotated)


def format_summary(summary: DiffSummary) -> str:
    lines: List[str] = []
    lines.append("=== Diff Summary ===")
    lines.append(f"Risk label : {summary.score.label}")
    lines.append(f"Total score: {summary.score.total}")
    lines.append(f"Changes    : {summary.total_changes}")

    critical = summary.critical_keys()
    if critical:
        lines.append(f"Critical   : {', '.join(critical)}")

    high = summary.high_keys()
    if high:
        lines.append(f"High risk  : {', '.join(high)}")

    by_cat: dict[str, int] = {}
    for ann in summary.annotated.annotations:
        by_cat[ann.category] = by_cat.get(ann.category, 0) + 1
    if by_cat:
        cat_str = ", ".join(f"{k}:{v}" for k, v in sorted(by_cat.items()))
        lines.append(f"Categories : {cat_str}")

    return "\n".join(lines)


def summary_as_dict(summary: DiffSummary) -> dict:
    return {
        "risk_label": summary.score.label,
        "total_score": summary.score.total,
        "total_changes": summary.total_changes,
        "critical_keys": summary.critical_keys(),
        "high_keys": summary.high_keys(),
        "categories": {
            ann.key: ann.category for ann in summary.annotated.annotations
        },
    }
