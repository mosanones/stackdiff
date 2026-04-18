import pytest
from stackdiff.alerter import (
    Alert, AlertRule, evaluate_rules, format_alerts, DEFAULT_RULES
)
from stackdiff.scorer import DiffScore
from stackdiff.summarizer import DiffSummary


@pytest.fixture
def clean_score():
    return DiffScore(score=0.0, label="clean", breakdown={})


@pytest.fixture
def high_score():
    return DiffScore(score=85.0, label="high-risk", breakdown={})


@pytest.fixture
def breaking_score():
    return DiffScore(score=95.0, label="breaking", breakdown={})


@pytest.fixture
def empty_summary():
    return DiffSummary(total_changes=0, critical_keys=[], high_keys=[], label="clean", score=0.0)


@pytest.fixture
def critical_summary():
    return DiffSummary(total_changes=3, critical_keys=["db.password"], high_keys=[], label="high-risk", score=85.0)


def test_no_alerts_for_clean(clean_score, empty_summary):
    alerts = evaluate_rules(clean_score, empty_summary, rules=DEFAULT_RULES)
    assert alerts == []


def test_alert_triggered_on_high_score(high_score, empty_summary):
    rule = AlertRule(name="high_score", min_score=70.0)
    alerts = evaluate_rules(high_score, empty_summary, rules=[rule])
    assert len(alerts) == 1
    assert alerts[0].rule_name == "high_score"
    assert alerts[0].severity == "warning"


def test_alert_critical_severity_above_90(breaking_score, empty_summary):
    rule = AlertRule(name="high_score", min_score=70.0)
    alerts = evaluate_rules(breaking_score, empty_summary, rules=[rule])
    assert alerts[0].severity == "critical"


def test_alert_on_critical_keys(clean_score, critical_summary):
    rule = AlertRule(name="critical_keys_changed", require_critical=True)
    alerts = evaluate_rules(clean_score, critical_summary, rules=[rule])
    assert len(alerts) == 1
    assert "db.password" in alerts[0].message


def test_no_alert_when_no_critical_keys(clean_score, empty_summary):
    rule = AlertRule(name="critical_keys_changed", require_critical=True)
    alerts = evaluate_rules(clean_score, empty_summary, rules=[rule])
    assert alerts == []


def test_alert_on_label_match(breaking_score, empty_summary):
    rule = AlertRule(name="breaking_label", require_label="breaking")
    alerts = evaluate_rules(breaking_score, empty_summary, rules=[rule])
    assert len(alerts) == 1
    assert alerts[0].severity == "warning"


def test_no_alert_on_label_mismatch(high_score, empty_summary):
    """Rule requiring 'breaking' label should not fire for 'high-risk' label."""
    rule = AlertRule(name="breaking_label", require_label="breaking")
    alerts = evaluate_rules(high_score, empty_summary, rules=[rule])
    assert alerts == []


def test_format_alerts_no_alerts():
    assert format_alerts([]) == "No alerts triggered."


def test_format_alerts_shows_entries():
    a = Alert(rule_name="r", message="msg", severity="critical")
    out = format_alerts([a])
    assert "[CRITICAL]" in out
    assert "msg" in out


def test_format_alerts_multiple_entries():
    """All alerts should appear in formatted output."""
    alerts = [
        Alert(rule_name="r1", message="first", severity="warning"),
        Alert(rule_name="r2", message="second", severity="critical"),
    ]
    out = format_alerts(alerts)
    assert "first" in out
    assert "second" in out
    assert "[WARNING]" in out
    assert "[CRITICAL]" in out


def test_alert_as_dict():
    a = Alert(rule_name="r", message="m", severity="info")
    d = a.as_dict()
    assert d == {"rule": "r", "message": "m", "severity": "info"}
