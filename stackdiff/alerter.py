"""Alert rules engine: raise alerts when diff score exceeds thresholds."""
from dataclasses import dataclass, field
from typing import List, Optional
from stackdiff.scorer import DiffScore
from stackdiff.summarizer import DiffSummary


@dataclass
class AlertRule:
    name: str
    min_score: Optional[float] = None
    require_critical: bool = False
    require_label: Optional[str] = None


@dataclass
class Alert:
    rule_name: str
    message: str
    severity: str  # "critical" | "warning" | "info"

    def as_dict(self) -> dict:
        return {"rule": self.rule_name, "message": self.message, "severity": self.severity}


DEFAULT_RULES: List[AlertRule] = [
    AlertRule(name="high_score", min_score=70.0),
    AlertRule(name="critical_keys_changed", require_critical=True),
    AlertRule(name="breaking_label", require_label="breaking"),
]


def evaluate_rules(
    score: DiffScore,
    summary: DiffSummary,
    rules: Optional[List[AlertRule]] = None,
) -> List[Alert]:
    if rules is None:
        rules = DEFAULT_RULES
    alerts: List[Alert] = []
    for rule in rules:
        if rule.min_score is not None and score.score >= rule.min_score:
            alerts.append(Alert(
                rule_name=rule.name,
                message=f"Diff score {score.score:.1f} exceeds threshold {rule.min_score}",
                severity="critical" if score.score >= 90 else "warning",
            ))
        if rule.require_critical and summary.critical_keys:
            alerts.append(Alert(
                rule_name=rule.name,
                message=f"Critical keys changed: {', '.join(summary.critical_keys)}",
                severity="critical",
            ))
        if rule.require_label and score.label == rule.require_label:
            alerts.append(Alert(
                rule_name=rule.name,
                message=f"Diff labelled '{rule.require_label}'",
                severity="warning",
            ))
    return alerts


def format_alerts(alerts: List[Alert]) -> str:
    if not alerts:
        return "No alerts triggered."
    lines = ["ALERTS:"]
    for a in alerts:
        lines.append(f"  [{a.severity.upper()}] {a.rule_name}: {a.message}")
    return "\n".join(lines)
