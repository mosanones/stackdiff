"""Tests for stackdiff.recommender_formatter."""
import json
import pytest
from stackdiff.diff_recommender import Recommendation, RecommendationReport
from stackdiff.recommender_formatter import (
    format_recommendations_text,
    format_recommendations_json,
    format_recommendations_output,
)


@pytest.fixture
def report_with_items():
    return RecommendationReport(
        recommendations=[
            Recommendation(
                key="db.password",
                message="[security] Key 'db.password' changed",
                priority="high",
                action="Review immediately.",
            ),
            Recommendation(
                key="app.debug",
                message="[config] Key 'app.debug' changed",
                priority="low",
                action="Confirm it is expected.",
            ),
        ]
    )


@pytest.fixture
def empty_report():
    return RecommendationReport(recommendations=[])


def test_text_format_empty_report(empty_report):
    out = format_recommendations_text(empty_report)
    assert "No recommendations" in out


def test_text_format_contains_header(report_with_items):
    out = format_recommendations_text(report_with_items)
    assert "=== Recommendations ===" in out


def test_text_format_shows_key(report_with_items):
    out = format_recommendations_text(report_with_items)
    assert "db.password" in out


def test_text_format_shows_priority(report_with_items):
    out = format_recommendations_text(report_with_items)
    assert "HIGH" in out
    assert "LOW" in out


def test_text_format_shows_action(report_with_items):
    out = format_recommendations_text(report_with_items)
    assert "Review immediately." in out


def test_text_format_shows_total_count(report_with_items):
    out = format_recommendations_text(report_with_items)
    assert "2 recommendation(s)" in out


def test_json_format_is_valid_json(report_with_items):
    out = format_recommendations_json(report_with_items)
    data = json.loads(out)
    assert "total" in data
    assert data["total"] == 2


def test_json_format_contains_recommendations(report_with_items):
    out = format_recommendations_json(report_with_items)
    data = json.loads(out)
    assert len(data["recommendations"]) == 2
    assert data["recommendations"][0]["key"] == "db.password"


def test_format_output_text(report_with_items):
    out = format_recommendations_output(report_with_items, fmt="text")
    assert "==" in out


def test_format_output_json(report_with_items):
    out = format_recommendations_output(report_with_items, fmt="json")
    data = json.loads(out)
    assert "recommendations" in data


def test_format_output_defaults_to_text(report_with_items):
    out = format_recommendations_output(report_with_items)
    assert "==" in out
