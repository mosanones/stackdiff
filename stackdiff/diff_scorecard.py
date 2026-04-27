"""diff_scorecard.py — builds a human-readable scorecard from a FullReport."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from stackdiff.diff_report_builder import FullReport


@dataclass
class ScorecardRow:
    category: str
    value: str
    status: str  # 'ok', 'warn', 'critical'

    def as_dict(self) -> dict:
        return {"category": self.category, "value": self.value, "status": self.status}


@dataclass
class Scorecard:
    label_a: str
    label_b: str
    rows: List[ScorecardRow] = field(default_factory=list)
    overall: str = "ok"

    def as_dict(self) -> dict:
        return {
            "label_a": self.label_a,
            "label_b": self.label_b,
            "overall": self.overall,
            "rows": [r.as_dict() for r in self.rows],
        }


def _overall(rows: List[ScorecardRow]) -> str:
    statuses = {r.status for r in rows}
    if "critical" in statuses:
        return "critical"
    if "warn" in statuses:
        return "warn"
    return "ok"


def _status_for_score(score: float) -> str:
    if score >= 70:
        return "critical"
    if score >= 30:
        return "warn"
    return "ok"


def build_scorecard(report: FullReport) -> Scorecard:
    """Derive a Scorecard from a FullReport."""
    rows: List[ScorecardRow] = []

    # Total changes
    total = report.stats.total_keys
    rows.append(ScorecardRow(
        category="Total changes",
        value=str(total),
        status="ok" if total == 0 else ("critical" if total >= 10 else "warn"),
    ))

    # Risk score
    risk = report.score.score
    rows.append(ScorecardRow(
        category="Risk score",
        value=f"{risk:.1f} ({report.score.label})",
        status=_status_for_score(risk),
    ))

    # Alerts
    alert_count = len(report.alerts)
    rows.append(ScorecardRow(
        category="Alerts",
        value=str(alert_count),
        status="critical" if alert_count > 0 else "ok",
    ))

    # Critical annotations
    critical = report.summary.critical_keys
    rows.append(ScorecardRow(
        category="Critical keys",
        value=str(len(critical)),
        status="critical" if critical else "ok",
    ))

    overall = _overall(rows)
    return Scorecard(
        label_a=report.label_a,
        label_b=report.label_b,
        rows=rows,
        overall=overall,
    )
