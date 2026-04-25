"""Tests for stackdiff.diff_recommender."""
import pytest
from unittest.mock import MagicMock
from stackdiff.diff_recommender import (
    Recommendation,
    RecommendationReport,
    generate_recommendations,
    _priority_from_severity,
)
from stackdiff.annotator import AnnotatedDiff, Annotation
from stackdiff.scorer import DiffScore
from stackdiff.diff_stats import DiffStats


def _make_annotation(key, severity="low", category="general", change_type="changed"):
    return Annotation(
        key=key,
        severity=severity,
        category=category,
        change_type=change_type,
        message=f"{key} was {change_type}",
    )


@pytest.fixture
def annotated_with_critical():
    anns = [
        _make_annotation("db.password", severity="critical", category="security"),
        _make_annotation("app.port", severity="low", category="network"),
    ]
    return AnnotatedDiff(annotations=anns)


@pytest.fixture
def empty_annotated():
    return AnnotatedDiff(annotations=[])


def test_recommendation_as_dict():
    rec = Recommendation(key="k", message="m", priority="high", action="a")
    d = rec.as_dict()
    assert d["key"] == "k"
    assert d["priority"] == "high"
    assert d["action"] == "a"


def test_report_high_priority_filter():
    recs = [
        Recommendation("a", "msg", "high", "act"),
        Recommendation("b", "msg", "low", "act"),
    ]
    report = RecommendationReport(recommendations=recs)
    assert len(report.high_priority()) == 1
    assert report.high_priority()[0].key == "a"


def test_report_as_dict_structure(annotated_with_critical):
    report = generate_recommendations(annotated_with_critical)
    d = report.as_dict()
    assert "total" in d
    assert "high_priority_count" in d
    assert "recommendations" in d
    assert isinstance(d["recommendations"], list)


def test_generate_recommendations_critical_is_high(annotated_with_critical):
    report = generate_recommendations(annotated_with_critical)
    keys = {r.key: r for r in report.recommendations}
    assert keys["db.password"].priority == "high"


def test_generate_recommendations_low_severity_is_low(annotated_with_critical):
    report = generate_recommendations(annotated_with_critical)
    keys = {r.key: r for r in report.recommendations}
    assert keys["app.port"].priority == "low"


def test_generate_recommendations_empty_annotated(empty_annotated):
    report = generate_recommendations(empty_annotated)
    assert report.recommendations == []


def test_high_score_adds_score_recommendation(empty_annotated):
    score = DiffScore(total_score=80, label="high-risk", breakdown={})
    report = generate_recommendations(empty_annotated, score=score)
    keys = [r.key for r in report.recommendations]
    assert "__score__" in keys


def test_low_score_no_score_recommendation(empty_annotated):
    score = DiffScore(total_score=10, label="clean", breakdown={})
    report = generate_recommendations(empty_annotated, score=score)
    keys = [r.key for r in report.recommendations]
    assert "__score__" not in keys


def test_large_stats_adds_stats_recommendation(empty_annotated):
    stats = DiffStats(total_keys=25, added_count=10, removed_count=5, changed_count=10)
    report = generate_recommendations(empty_annotated, stats=stats)
    keys = [r.key for r in report.recommendations]
    assert "__stats__" in keys


def test_priority_from_severity_mapping():
    assert _priority_from_severity("critical") == "high"
    assert _priority_from_severity("high") == "high"
    assert _priority_from_severity("medium") == "medium"
    assert _priority_from_severity("low") == "low"
    assert _priority_from_severity("unknown") == "low"


def test_recommendations_sorted_high_first(annotated_with_critical):
    report = generate_recommendations(annotated_with_critical)
    priorities = [r.priority for r in report.recommendations]
    order = ["high", "medium", "low"]
    indices = [order.index(p) for p in priorities]
    assert indices == sorted(indices)
