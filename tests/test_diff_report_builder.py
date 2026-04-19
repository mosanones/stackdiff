import pytest
from stackdiff.diff_engine import DiffResult
from stackdiff.annotator import annotate_diff
from stackdiff.diff_report_builder import build_full_report, FullReport, DEFAULT_RULES
from stackdiff.alerter import AlertRule
from stackdiff.report_formatter import format_full_text, format_full_json, format_full_output


@pytest.fixture
def simple_diff():
    return DiffResult(
        removed={"db.password": "secret"},
        added={"db.password": "newsecret"},
        changed={"db.password": ("secret", "newsecret")},
        unchanged={"app.name": "myapp"},
    )


@pytest.fixture
def annotated(simple_diff):
    return annotate_diff(simple_diff)


def test_build_full_report_returns_full_report(annotated):
    report = build_full_report(annotated)
    assert isinstance(report, FullReport)


def test_full_report_stats_total(annotated):
    report = build_full_report(annotated)
    assert report.stats.total_keys >= 1


def test_full_report_score_is_numeric(annotated):
    report = build_full_report(annotated)
    assert isinstance(report.score.score, (int, float))


def test_full_report_has_alerts_for_critical(annotated):
    report = build_full_report(annotated)
    assert report.has_alerts


def test_full_report_no_alerts_when_no_rules(annotated):
    report = build_full_report(annotated, rules=[])
    assert not report.has_alerts


def test_as_dict_keys(annotated):
    report = build_full_report(annotated)
    d = report.as_dict()
    assert set(d.keys()) == {"stats", "score", "summary", "alerts"}


def test_format_full_text_contains_header(annotated):
    report = build_full_report(annotated)
    text = format_full_text(report, label_a="staging", label_b="prod")
    assert "staging" in text and "prod" in text


def test_format_full_text_shows_risk(annotated):
    report = build_full_report(annotated)
    text = format_full_text(report)
    assert "Risk Score" in text


def test_format_full_json_is_valid(annotated):
    import json
    report = build_full_report(annotated)
    data = json.loads(format_full_json(report))
    assert "score" in data


def test_format_full_output_json(annotated):
    report = build_full_report(annotated)
    out = format_full_output(report, fmt="json")
    assert out.startswith("{")


def test_format_full_output_text_default(annotated):
    report = build_full_report(annotated)
    out = format_full_output(report)
    assert "Diff Report" in out
