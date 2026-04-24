"""Tests for diff_comparator.py and comparator_formatter.py."""
from __future__ import annotations

import json
import pytest

from stackdiff.diff_engine import DiffResult
from stackdiff.diff_comparator import compare_diffs, ComparisonResult
from stackdiff.comparator_formatter import (
    format_comparison_text,
    format_comparison_json,
    format_comparison_output,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def base_left():
    return {"db.host": "localhost", "app.port": "8080"}


@pytest.fixture()
def base_right():
    return {"db.host": "prod-db", "app.port": "8080", "app.debug": "false"}


@pytest.fixture()
def prev_diff(base_left, base_right):
    from stackdiff.diff_engine import diff_configs
    return diff_configs(base_left, base_right)


@pytest.fixture()
def curr_diff_same(base_left, base_right):
    from stackdiff.diff_engine import diff_configs
    return diff_configs(base_left, base_right)


@pytest.fixture()
def curr_diff_regression(base_left):
    from stackdiff.diff_engine import diff_configs
    right = {"db.host": "prod-db", "app.port": "9090", "new.key": "val"}
    return diff_configs(base_left, right)


# ---------------------------------------------------------------------------
# compare_diffs
# ---------------------------------------------------------------------------

def test_compare_no_previous_returns_all_as_new(curr_diff_regression):
    result = compare_diffs(None, curr_diff_regression)
    assert isinstance(result, ComparisonResult)
    assert set(result.new_keys) == set(curr_diff_regression.removed | curr_diff_regression.added | curr_diff_regression.changed)


def test_compare_identical_diffs_no_new_or_resolved(prev_diff, curr_diff_same):
    result = compare_diffs(prev_diff, curr_diff_same)
    assert result.new_keys == []
    assert result.resolved_keys == []


def test_compare_regression_detected(prev_diff, curr_diff_regression):
    result = compare_diffs(prev_diff, curr_diff_regression)
    assert result.is_regression


def test_compare_resolved_keys_when_diff_shrinks(prev_diff, base_left):
    from stackdiff.diff_engine import diff_configs
    # current diff has no changes
    curr = diff_configs(base_left, base_left)
    result = compare_diffs(prev_diff, curr)
    assert result.is_improved
    assert not result.is_regression


def test_compare_persisting_keys_present(prev_diff, curr_diff_same):
    result = compare_diffs(prev_diff, curr_diff_same)
    assert len(result.persisting_keys) > 0


def test_as_dict_contains_expected_keys(prev_diff, curr_diff_same):
    result = compare_diffs(prev_diff, curr_diff_same)
    d = result.as_dict()
    for key in ("new_keys", "resolved_keys", "persisting_keys", "changed_values", "is_regression", "is_improved"):
        assert key in d


# ---------------------------------------------------------------------------
# Formatters
# ---------------------------------------------------------------------------

def test_format_text_contains_header(prev_diff, curr_diff_same):
    result = compare_diffs(prev_diff, curr_diff_same)
    text = format_comparison_text(result)
    assert "Diff Comparison" in text


def test_format_text_shows_status(prev_diff, curr_diff_regression):
    result = compare_diffs(prev_diff, curr_diff_regression)
    text = format_comparison_text(result)
    assert "REGRESSION" in text


def test_format_json_is_valid_json(prev_diff, curr_diff_same):
    result = compare_diffs(prev_diff, curr_diff_same)
    raw = format_comparison_json(result)
    parsed = json.loads(raw)
    assert "is_regression" in parsed


def test_format_output_delegates_to_json(prev_diff, curr_diff_same):
    result = compare_diffs(prev_diff, curr_diff_same)
    out = format_comparison_output(result, fmt="json")
    parsed = json.loads(out)
    assert isinstance(parsed, dict)


def test_format_output_defaults_to_text(prev_diff, curr_diff_same):
    result = compare_diffs(prev_diff, curr_diff_same)
    out = format_comparison_output(result)
    assert "==" in out
