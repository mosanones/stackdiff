"""Combines diff stats, score, summary, and alerts into a unified report dict."""

from dataclasses import dataclass, field
from typing import Any

from stackdiff.diff_stats import DiffStats, compute_stats
from stackdiff.scorer import DiffScore, score_annotated
from stackdiff.summarizer import DiffSummary, build_summary
from stackdiff.alerter import Alert, AlertRule, evaluate_rules
from stackdiff.annotator import AnnotatedDiff


DEFAULT_RULES: list[AlertRule] = [
    AlertRule(name="high_risk", condition="score >= 70", threshold=70),
    AlertRule(name="critical_keys", condition="critical_keys > 0", threshold=0),
]


@dataclass
class FullReport:
    stats: DiffStats
    score: DiffScore
    summary: DiffSummary
    alerts: list[Alert] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "stats": self.stats.as_dict(),
            "score": self.score.as_dict(),
            "summary": self.summary.as_dict(),
            "alerts": [a.as_dict() for a in self.alerts],
        }

    @property
    def has_alerts(self) -> bool:
        return len(self.alerts) > 0


def build_full_report(
    annotated: AnnotatedDiff,
    rules: list[AlertRule] | None = None,
) -> FullReport:
    """Build a FullReport from an AnnotatedDiff."""
    stats = compute_stats(annotated.diff)
    score = score_annotated(annotated)
    summary = build_summary(score, annotated)
    active_rules = rules if rules is not None else DEFAULT_RULES
    alerts = evaluate_rules(summary, active_rules)
    return FullReport(stats=stats, score=score, summary=summary, alerts=alerts)
