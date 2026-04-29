"""diff_spotlight: highlight the most significant changes in a diff."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from stackdiff.diff_engine import DiffResult
from stackdiff.annotator import AnnotatedDiff, annotate_diff
from stackdiff.scorer import score_annotated


@dataclass
class SpotlightEntry:
    key: str
    old_value: Optional[str]
    new_value: Optional[str]
    severity: str
    reason: str

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "severity": self.severity,
            "reason": self.reason,
        }


@dataclass
class DiffSpotlight:
    entries: List[SpotlightEntry] = field(default_factory=list)
    total_score: float = 0.0

    @property
    def top(self) -> Optional[SpotlightEntry]:
        return self.entries[0] if self.entries else None

    def as_dict(self) -> dict:
        return {
            "total_score": self.total_score,
            "entries": [e.as_dict() for e in self.entries],
        }


_SEVERITY_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}


def _reason(severity: str, key: str) -> str:
    if severity == "critical":
        return f"'{key}' is a critical secret or credential change"
    if severity == "high":
        return f"'{key}' is a high-impact endpoint or service key"
    if severity == "medium":
        return f"'{key}' affects application behaviour"
    return f"'{key}' is a minor configuration change"


def build_spotlight(
    diff: DiffResult,
    annotated: Optional[AnnotatedDiff] = None,
    top_n: int = 5,
) -> DiffSpotlight:
    """Return the top-N most significant changes from *diff*."""
    if annotated is None:
        annotated = annotate_diff(diff)

    score = score_annotated(annotated)

    entries: List[SpotlightEntry] = []
    for ann in annotated.annotations:
        old_val = diff.removed.get(ann.key) or (diff.changed.get(ann.key) or (None, None))[0]
        new_val = diff.added.get(ann.key) or (diff.changed.get(ann.key) or (None, None))[1]
        entries.append(
            SpotlightEntry(
                key=ann.key,
                old_value=str(old_val) if old_val is not None else None,
                new_value=str(new_val) if new_val is not None else None,
                severity=ann.severity,
                reason=_reason(ann.severity, ann.key),
            )
        )

    entries.sort(key=lambda e: (_SEVERITY_RANK.get(e.severity, 99), e.key))
    return DiffSpotlight(entries=entries[:top_n], total_score=score.value)
