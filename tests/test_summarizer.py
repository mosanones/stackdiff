"""Tests for stackdiff.summarizer."""
import pytest

from stackdiff.diff_engine import DiffResult
from stackdiff.annotator import Annotation, AnnotatedDiff
from stackdiff.scorer import DiffScore
from stackdiff.summarizer import build_summary, format_summary, summary_as_dict


@pytest.fixture()
def score():
    return DiffScore(total=18, breakdown={"critical": 10, "high": 8}, label="high-risk")


@pytest.fixture()
def annotated():
    diff = DiffResult(
        removed={"db.password": "secret"},
        added={"db.password": "newsecret"},
        changed={"api.endpoint": ("http://old", "http://new")},
    )
    annotations = [
        Annotation(key="db.password", severity="critical", category="secret"),
        Annotation(key="api.endpoint", severity="high", category="endpoint"),
    ]
    return AnnotatedDiff(diff_result=diff, annotations=annotations)


def test_build_summary_returns_diff_summary(score, annotated):
    s = build_summary(score, annotated)
    assert s.score is score
    assert s.annotated is annotated


def test_total_changes(score, annotated):
    s = build_summary(score, annotated)
    # removed 1 + added 1 + changed 1
    assert s.total_changes == 3


def test_critical_keys(score, annotated):
    s = build_summary(score, annotated)
    assert s.critical_keys() == ["db.password"]


def test_high_keys(score, annotated):
    s = build_summary(score, annotated)
    assert s.high_keys() == ["api.endpoint"]


def test_format_summary_contains_label(score, annotated):
    text = format_summary(build_summary(score, annotated))
    assert "high-risk" in text


def test_format_summary_contains_score(score, annotated):
    text = format_summary(build_summary(score, annotated))
    assert "18" in text


def test_format_summary_shows_critical(score, annotated):
    text = format_summary(build_summary(score, annotated))
    assert "db.password" in text


def test_format_summary_shows_categories(score, annotated):
    text = format_summary(build_summary(score, annotated))
    assert "secret" in text
    assert "endpoint" in text


def test_summary_as_dict_structure(score, annotated):
    d = summary_as_dict(build_summary(score, annotated))
    assert d["risk_label"] == "high-risk"
    assert d["total_score"] == 18
    assert "db.password" in d["critical_keys"]
    assert "api.endpoint" in d["high_keys"]
    assert isinstance(d["categories"], dict)
