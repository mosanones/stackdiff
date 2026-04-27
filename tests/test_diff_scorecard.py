"""Tests for stackdiff.diff_scorecard."""
import pytest

from stackdiff.diff_engine import DiffResult
from stackdiff.diff_report_builder import build_full_report
from stackdiff.diff_scorecard import (
    Scorecard,
    ScorecardRow,
    build_scorecard,
    _overall,
    _status_for_score,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def clean_diff() -> DiffResult:
    return DiffResult(label_a="staging", label_b="prod", removed={}, added={}, changed={})


@pytest.fixture()
def dirty_diff() -> DiffResult:
    return DiffResult(
        label_a="staging",
        label_b="prod",
        removed={"db.host": "old"},
        added={"db.host": "new"},
        changed={"api.password": ("s3cr3t", "n3ws3cr3t"), "app.endpoint": ("http://a", "http://b")},
    )


# ---------------------------------------------------------------------------
# Unit helpers
# ---------------------------------------------------------------------------

def test_status_for_score_ok():
    assert _status_for_score(0) == "ok"
    assert _status_for_score(29.9) == "ok"


def test_status_for_score_warn():
    assert _status_for_score(30) == "warn"
    assert _status_for_score(69.9) == "warn"


def test_status_for_score_critical():
    assert _status_for_score(70) == "critical"
    assert _status_for_score(100) == "critical"


def test_overall_ok():
    rows = [ScorecardRow("a", "1", "ok"), ScorecardRow("b", "2", "ok")]
    assert _overall(rows) == "ok"


def test_overall_warn():
    rows = [ScorecardRow("a", "1", "ok"), ScorecardRow("b", "2", "warn")]
    assert _overall(rows) == "warn"


def test_overall_critical_dominates():
    rows = [ScorecardRow("a", "1", "warn"), ScorecardRow("b", "2", "critical")]
    assert _overall(rows) == "critical"


# ---------------------------------------------------------------------------
# build_scorecard
# ---------------------------------------------------------------------------

def test_build_scorecard_returns_scorecard(clean_diff):
    report = build_full_report(clean_diff)
    sc = build_scorecard(report)
    assert isinstance(sc, Scorecard)


def test_build_scorecard_clean_overall_ok(clean_diff):
    report = build_full_report(clean_diff)
    sc = build_scorecard(report)
    assert sc.overall == "ok"


def test_build_scorecard_dirty_overall_not_ok(dirty_diff):
    report = build_full_report(dirty_diff)
    sc = build_scorecard(report)
    assert sc.overall in ("warn", "critical")


def test_build_scorecard_has_four_rows(clean_diff):
    report = build_full_report(clean_diff)
    sc = build_scorecard(report)
    assert len(sc.rows) == 4


def test_scorecard_labels_preserved(dirty_diff):
    report = build_full_report(dirty_diff)
    sc = build_scorecard(report)
    assert sc.label_a == "staging"
    assert sc.label_b == "prod"


def test_scorecard_as_dict_keys(clean_diff):
    report = build_full_report(clean_diff)
    sc = build_scorecard(report)
    d = sc.as_dict()
    assert set(d.keys()) == {"label_a", "label_b", "overall", "rows"}


def test_scorecard_row_as_dict_keys(clean_diff):
    report = build_full_report(clean_diff)
    sc = build_scorecard(report)
    row_d = sc.rows[0].as_dict()
    assert set(row_d.keys()) == {"category", "value", "status"}


def test_scorecard_total_changes_category_present(dirty_diff):
    report = build_full_report(dirty_diff)
    sc = build_scorecard(report)
    categories = [r.category for r in sc.rows]
    assert "Total changes" in categories
