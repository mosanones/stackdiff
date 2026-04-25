"""Generates actionable recommendations based on diff analysis."""
from dataclasses import dataclass, field
from typing import List, Optional
from stackdiff.annotator import AnnotatedDiff
from stackdiff.scorer import DiffScore
from stackdiff.diff_stats import DiffStats


@dataclass
class Recommendation:
    key: str
    message: str
    priority: str  # "high", "medium", "low"
    action: str

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "message": self.message,
            "priority": self.priority,
            "action": self.action,
        }


@dataclass
class RecommendationReport:
    recommendations: List[Recommendation] = field(default_factory=list)

    def high_priority(self) -> List[Recommendation]:
        return [r for r in self.recommendations if r.priority == "high"]

    def as_dict(self) -> dict:
        return {
            "total": len(self.recommendations),
            "high_priority_count": len(self.high_priority()),
            "recommendations": [r.as_dict() for r in self.recommendations],
        }


_ACTION_MAP = {
    "critical": "Immediately review and verify this change before deploying.",
    "high": "Review this change carefully; consider a staged rollout.",
    "medium": "Verify this change is intentional and documented.",
    "low": "Low-risk change; confirm it is expected.",
}


def _priority_from_severity(severity: str) -> str:
    return {"critical": "high", "high": "high", "medium": "medium"}.get(severity, "low")


def generate_recommendations(
    annotated: AnnotatedDiff,
    score: Optional[DiffScore] = None,
    stats: Optional[DiffStats] = None,
) -> RecommendationReport:
    recs: List[Recommendation] = []

    for ann in annotated.annotations:
        priority = _priority_from_severity(ann.severity)
        action = _ACTION_MAP.get(ann.severity, _ACTION_MAP["low"])
        msg = (
            f"[{ann.category}] Key '{ann.key}' changed "
            f"({ann.change_type}): {ann.message}"
        )
        recs.append(Recommendation(key=ann.key, message=msg, priority=priority, action=action))

    if score and score.total_score >= 70:
        recs.append(
            Recommendation(
                key="__score__",
                message=f"Overall diff risk score is {score.total_score} ({score.label}).",
                priority="high",
                action="Conduct a full review before promoting to production.",
            )
        )

    if stats and stats.total_keys > 20:
        recs.append(
            Recommendation(
                key="__stats__",
                message=f"Large diff detected: {stats.total_keys} keys changed.",
                priority="medium",
                action="Consider breaking this deployment into smaller increments.",
            )
        )

    recs.sort(key=lambda r: ["high", "medium", "low"].index(r.priority))
    return RecommendationReport(recommendations=recs)
