"""Tests for diff_outlier and outlier_formatter."""
import json
import pytest

from stackdiff.diff_engine import DiffResult
from stackdiff.diff_outlier import detect_outliers, DiffOutliers, OutlierEntry
from stackdiff.outlier_formatter import (
    format_outlier_text,
    format_outlier_json,
    format_outlier_output,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def dr_common():
    """A DiffResult where 'db.host' changed — appears in most diffs."""
    return DiffResult(
        removed={"db.host": "old-db"},
        added={"db.host": "new-db"},
        changed={},
    )


@pytest.fixture()
def dr_rare():
    """A DiffResult where only 'secret.key' changed — outlier."""
    return DiffResult(
        removed={"secret.key": "abc"},
        added={"secret.key": "xyz"},
        changed={},
    )


@pytest.fixture()
def many_diffs(dr_common, dr_rare):
    """4 diffs: db.host changes in all 4, secret.key only in 1."""
    return [dr_common, dr_common, dr_common, dr_rare]


# ---------------------------------------------------------------------------
# detect_outliers
# ---------------------------------------------------------------------------

def test_detect_outliers_returns_diff_outliers(many_diffs):
    result = detect_outliers(many_diffs)
    assert isinstance(result, DiffOutliers)


def test_detect_outliers_empty_input():
    result = detect_outliers([])
    assert result.total_diffs == 0
    assert result.outliers == []


def test_total_diffs_recorded(many_diffs):
    result = detect_outliers(many_diffs)
    assert result.total_diffs == 4


def test_outlier_key_detected(many_diffs):
    result = detect_outliers(many_diffs, threshold=0.5)
    keys = [e.key for e in result.outliers]
    assert "secret.key" in keys


def test_common_key_not_outlier(many_diffs):
    result = detect_outliers(many_diffs, threshold=0.5)
    keys = [e.key for e in result.outliers]
    assert "db.host" not in keys


def test_frequency_calculated_correctly(many_diffs):
    result = detect_outliers(many_diffs, threshold=0.5)
    entry = next(e for e in result.outliers if e.key == "secret.key")
    assert entry.frequency == pytest.approx(0.25)
    assert entry.change_count == 1


def test_top_returns_limited_entries(many_diffs):
    result = detect_outliers(many_diffs, threshold=1.0)  # all keys are outliers
    top = result.top(n=1)
    assert len(top) <= 1


def test_as_dict_has_expected_keys(many_diffs):
    result = detect_outliers(many_diffs)
    d = result.as_dict()
    assert "total_diffs" in d
    assert "threshold" in d
    assert "outliers" in d


def test_outlier_entry_as_dict():
    entry = OutlierEntry(
        key="app.debug",
        change_count=1,
        total_diffs=5,
        frequency=0.2,
        sample_removed="false",
        sample_added="true",
    )
    d = entry.as_dict()
    assert d["key"] == "app.debug"
    assert d["frequency"] == pytest.approx(0.2)


# ---------------------------------------------------------------------------
# outlier_formatter
# ---------------------------------------------------------------------------

def test_text_format_contains_header(many_diffs):
    result = detect_outliers(many_diffs)
    text = format_outlier_text(result)
    assert "Outlier Detection" in text


def test_text_format_no_outliers():
    empty = DiffOutliers(total_diffs=0, threshold=0.5, outliers=[])
    text = format_outlier_text(empty)
    assert "No outlier keys detected" in text


def test_text_format_shows_outlier_key(many_diffs):
    result = detect_outliers(many_diffs, threshold=0.5)
    text = format_outlier_text(result)
    assert "secret.key" in text


def test_json_format_is_valid_json(many_diffs):
    result = detect_outliers(many_diffs)
    raw = format_outlier_json(result)
    parsed = json.loads(raw)
    assert "outliers" in parsed


def test_format_output_text(many_diffs):
    result = detect_outliers(many_diffs)
    out = format_outlier_output(result, fmt="text")
    assert "Outlier Detection" in out


def test_format_output_json(many_diffs):
    result = detect_outliers(many_diffs)
    out = format_outlier_output(result, fmt="json")
    parsed = json.loads(out)
    assert isinstance(parsed["outliers"], list)
