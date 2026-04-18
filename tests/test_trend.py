"""Tests for stackdiff.trend module."""
import pytest
from pathlib import Path
from stackdiff.trend import (
    TrendEntry,
    TrendReport,
    record_entry,
    load_trend,
    summarize_trend,
)


@pytest.fixture
def trend_dir(tmp_path):
    return tmp_path / "trends"


@pytest.fixture
def entry():
    return TrendEntry(
        timestamp="2024-01-01T00:00:00",
        label="low-risk",
        score=15,
        total_changes=3,
        critical=0,
        high=1,
    )


def test_entry_as_dict(entry):
    d = entry.as_dict()
    assert d["score"] == 15
    assert d["label"] == "low-risk"
    assert d["total_changes"] == 3


def test_record_and_load(trend_dir, entry):
    record_entry("prod", entry, trend_dir=trend_dir)
    report = load_trend("prod", trend_dir=trend_dir)
    assert len(report.entries) == 1
    assert report.entries[0].score == 15


def test_load_missing_returns_empty(trend_dir):
    report = load_trend("nonexistent", trend_dir=trend_dir)
    assert report.entries == []
    assert report.latest() is None


def test_multiple_entries_accumulated(trend_dir, entry):
    record_entry("prod", entry, trend_dir=trend_dir)
    entry2 = TrendEntry(
        timestamp="2024-01-02T00:00:00",
        label="moderate",
        score=40,
        total_changes=8,
        critical=1,
        high=2,
    )
    record_entry("prod", entry2, trend_dir=trend_dir)
    report = load_trend("prod", trend_dir=trend_dir)
    assert len(report.entries) == 2
    assert report.latest().label == "moderate"


def test_summarize_trend(trend_dir, entry):
    record_entry("prod", entry, trend_dir=trend_dir)
    report = load_trend("prod", trend_dir=trend_dir)
    summary = summarize_trend(report)
    assert summary["count"] == 1
    assert summary["min_score"] == 15
    assert summary["latest_label"] == "low-risk"


def test_summarize_empty_trend():
    report = TrendReport()
    result = summarize_trend(report)
    assert result["status"] == "no data"


def test_trend_report_as_dict(entry):
    report = TrendReport(entries=[entry])
    d = report.as_dict()
    assert "entries" in d
    assert len(d["entries"]) == 1
