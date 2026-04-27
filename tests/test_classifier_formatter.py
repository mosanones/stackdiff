"""Tests for stackdiff.classifier_formatter."""

from __future__ import annotations

import json
import pytest

from stackdiff.diff_classifier import ClassifiedDiff, ClassifiedKey
from stackdiff.classifier_formatter import (
    format_classified_text,
    format_classified_json,
    format_classified_output,
)


@pytest.fixture
def classified() -> ClassifiedDiff:
    return ClassifiedDiff(
        categories={
            "database": [
                ClassifiedKey("db_host", "database", "changed", "localhost", "prod-db"),
            ],
            "auth": [
                ClassifiedKey("api_key", "auth", "removed", "old-key", None),
                ClassifiedKey("token", "auth", "added", None, "new-token"),
            ],
        }
    )


@pytest.fixture
def empty_classified() -> ClassifiedDiff:
    return ClassifiedDiff(categories={})


def test_text_format_contains_header(classified):
    out = format_classified_text(classified)
    assert "Classified Diff" in out


def test_text_format_shows_category(classified):
    out = format_classified_text(classified)
    assert "[DATABASE]" in out
    assert "[AUTH]" in out


def test_text_format_shows_changed_key(classified):
    out = format_classified_text(classified)
    assert "db_host" in out
    assert "~" in out


def test_text_format_shows_removed_key(classified):
    out = format_classified_text(classified)
    assert "api_key" in out
    assert "-" in out


def test_text_format_shows_added_key(classified):
    out = format_classified_text(classified)
    assert "token" in out
    assert "+" in out


def test_text_format_empty_returns_no_diff_message(empty_classified):
    out = format_classified_text(empty_classified)
    assert "No differences" in out


def test_text_format_uses_custom_labels(classified):
    out = format_classified_text(classified, label_a="dev", label_b="prod")
    assert "dev" in out
    assert "prod" in out


def test_json_format_returns_valid_json(classified):
    out = format_classified_json(classified)
    data = json.loads(out)
    assert "database" in data
    assert "auth" in data


def test_json_format_empty(empty_classified):
    out = format_classified_json(empty_classified)
    assert json.loads(out) == {}


def test_format_classified_output_text(classified):
    out = format_classified_output(classified, fmt="text")
    assert "[DATABASE]" in out


def test_format_classified_output_json(classified):
    out = format_classified_output(classified, fmt="json")
    data = json.loads(out)
    assert "database" in data
