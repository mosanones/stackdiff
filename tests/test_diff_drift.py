"""Tests for stackdiff.diff_drift and stackdiff.drift_formatter."""
from __future__ import annotations

import json

import pytest

from stackdiff.diff_drift import DriftEntry, DriftReport, detect_drift
from stackdiff.drift_formatter import (
    format_drift_json,
    format_drift_output,
    format_drift_text,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def empty_history():
    return []


@pytest.fixture()
def single_run_history():
    return [
        {
            "timestamp": "2024-01-01T00:00:00",
            "removed": {"db.host": "old-host"},
            "added": {"db.host": "new-host"},
        }
    ]


@pytest.fixture()
def multi_run_history():
    return [
        {
            "timestamp": "2024-01-01T00:00:00",
            "removed": {"db.host": "host-a", "api.key": "key-1"},
            "added": {"db.host": "host-b", "api.key": "key-2"},
        },
        {
            "timestamp": "2024-01-02T00:00:00",
            "removed": {"db.host": "host-b"},
            "added": {"db.host": "host-c"},
        },
    ]


# ---------------------------------------------------------------------------
# detect_drift
# ---------------------------------------------------------------------------

def test_detect_drift_returns_drift_report(empty_history):
    result = detect_drift(empty_history)
    assert isinstance(result, DriftReport)


def test_detect_drift_empty_history_no_entries(empty_history):
    result = detect_drift(empty_history)
    assert result.entries == []
    assert result.total_runs == 0


def test_detect_drift_single_run_total_runs(single_run_history):
    result = detect_drift(single_run_history)
    assert result.total_runs == 1


def test_detect_drift_single_run_entry_count(single_run_history):
    result = detect_drift(single_run_history)
    assert len(result.entries) == 1


def test_detect_drift_single_run_key(single_run_history):
    result = detect_drift(single_run_history)
    assert result.entries[0].key == "db.host"


def test_detect_drift_single_run_change_count(single_run_history):
    result = detect_drift(single_run_history)
    assert result.entries[0].change_count == 1


def test_detect_drift_multi_run_drifting_key(multi_run_history):
    result = detect_drift(multi_run_history)
    assert "db.host" in result.drifting_keys


def test_detect_drift_multi_run_stable_key(multi_run_history):
    result = detect_drift(multi_run_history)
    assert "api.key" in result.stable_changed_keys


def test_detect_drift_multi_run_change_count(multi_run_history):
    result = detect_drift(multi_run_history)
    db_entry = next(e for e in result.entries if e.key == "db.host")
    assert db_entry.change_count == 2


def test_detect_drift_first_and_last_seen(multi_run_history):
    result = detect_drift(multi_run_history)
    db_entry = next(e for e in result.entries if e.key == "db.host")
    assert db_entry.first_seen == "2024-01-01T00:00:00"
    assert db_entry.last_seen == "2024-01-02T00:00:00"


def test_entry_as_dict_keys(single_run_history):
    result = detect_drift(single_run_history)
    d = result.entries[0].as_dict()
    assert set(d) == {"key", "change_count", "first_seen", "last_seen", "current_removed", "current_added"}


def test_report_as_dict_keys(single_run_history):
    result = detect_drift(single_run_history)
    d = result.as_dict()
    assert set(d) == {"total_runs", "drifting_keys", "stable_changed_keys", "entries"}


# ---------------------------------------------------------------------------
# drift_formatter
# ---------------------------------------------------------------------------

def test_format_drift_text_contains_header(single_run_history):
    report = detect_drift(single_run_history)
    out = format_drift_text(report)
    assert "Drift Report" in out


def test_format_drift_text_shows_key(single_run_history):
    report = detect_drift(single_run_history)
    out = format_drift_text(report)
    assert "db.host" in out


def test_format_drift_text_empty_message(empty_history):
    report = detect_drift(empty_history)
    out = format_drift_text(report)
    assert "No changes" in out


def test_format_drift_json_is_valid_json(multi_run_history):
    report = detect_drift(multi_run_history)
    out = format_drift_json(report)
    data = json.loads(out)
    assert "entries" in data


def test_format_drift_output_text(single_run_history):
    report = detect_drift(single_run_history)
    out = format_drift_output(report, fmt="text")
    assert "Drift Report" in out


def test_format_drift_output_json(single_run_history):
    report = detect_drift(single_run_history)
    out = format_drift_output(report, fmt="json")
    data = json.loads(out)
    assert data["total_runs"] == 1


def test_format_drift_text_drifting_marker(multi_run_history):
    report = detect_drift(multi_run_history)
    out = format_drift_text(report)
    # drifting key should have the asterisk marker
    assert "*" in out
