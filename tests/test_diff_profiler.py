"""Tests for stackdiff.diff_profiler."""

import time
import pytest

from stackdiff.diff_profiler import (
    DiffProfiler,
    ProfileEntry,
    ProfileReport,
    profile_pipeline,
)


# ---------------------------------------------------------------------------
# ProfileEntry
# ---------------------------------------------------------------------------

def test_profile_entry_as_dict():
    entry = ProfileEntry(stage="load", elapsed_ms=12.5, metadata={"keys": 10})
    d = entry.as_dict()
    assert d["stage"] == "load"
    assert d["elapsed_ms"] == 12.5
    assert d["metadata"] == {"keys": 10}


# ---------------------------------------------------------------------------
# ProfileReport
# ---------------------------------------------------------------------------

@pytest.fixture
def filled_report() -> ProfileReport:
    report = ProfileReport()
    report.entries = [
        ProfileEntry(stage="load", elapsed_ms=5.0),
        ProfileEntry(stage="diff", elapsed_ms=20.0),
        ProfileEntry(stage="format", elapsed_ms=3.0),
    ]
    return report


def test_total_ms(filled_report):
    assert filled_report.total_ms == pytest.approx(28.0)


def test_slowest_stage(filled_report):
    assert filled_report.slowest.stage == "diff"


def test_slowest_none_when_empty():
    assert ProfileReport().slowest is None


def test_report_as_dict(filled_report):
    d = filled_report.as_dict()
    assert d["total_ms"] == pytest.approx(28.0)
    assert d["slowest_stage"] == "diff"
    assert len(d["entries"]) == 3


# ---------------------------------------------------------------------------
# DiffProfiler
# ---------------------------------------------------------------------------

def test_profiler_records_entry():
    profiler = DiffProfiler()
    profiler.start_stage("load")
    time.sleep(0.01)
    entry = profiler.end_stage(metadata={"files": 2})
    assert entry.stage == "load"
    assert entry.elapsed_ms >= 5.0
    assert entry.metadata == {"files": 2}
    assert len(profiler.report.entries) == 1


def test_profiler_end_without_start_raises():
    profiler = DiffProfiler()
    with pytest.raises(RuntimeError, match="end_stage called without"):
        profiler.end_stage()


def test_profiler_multiple_stages():
    profiler = DiffProfiler()
    for stage in ("load", "diff", "format"):
        profiler.start_stage(stage)
        profiler.end_stage()
    assert len(profiler.report.entries) == 3
    assert profiler.report.entries[1].stage == "diff"


# ---------------------------------------------------------------------------
# profile_pipeline
# ---------------------------------------------------------------------------

def test_profile_pipeline_returns_report():
    calls = []
    fn_map = {
        "load": lambda: calls.append("load"),
        "diff": lambda: calls.append("diff"),
    }
    report = profile_pipeline(["load", "diff"], fn_map)
    assert isinstance(report, ProfileReport)
    assert calls == ["load", "diff"]
    assert len(report.entries) == 2


def test_profile_pipeline_missing_stage_raises():
    with pytest.raises(KeyError, match="missing"):
        profile_pipeline(["missing"], {})
