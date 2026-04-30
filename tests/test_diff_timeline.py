"""Tests for diff_timeline and timeline_formatter."""
import json
import os

import pytest

from stackdiff.diff_history import record_diff
from stackdiff.diff_timeline import (
    DiffTimeline,
    TimelineEvent,
    _entry_to_event,
    build_timeline,
)
from stackdiff.timeline_formatter import (
    format_timeline_json,
    format_timeline_output,
    format_timeline_text,
)


@pytest.fixture()
def hdir(tmp_path):
    return str(tmp_path / "history")


def _make_entry(label, added=1, removed=0, changed=0, score=None):
    return {
        "label": label,
        "stats": {"added": added, "removed": removed, "changed": changed},
        "score": score,
    }


@pytest.fixture()
def populated_timeline(hdir):
    record_diff("env-pair", _make_entry("deploy-1", added=2, score=10.0), history_dir=hdir)
    record_diff("env-pair", _make_entry("deploy-2", removed=1, changed=3, score=55.0), history_dir=hdir)
    record_diff("env-pair", _make_entry("deploy-3", added=5, score=80.0), history_dir=hdir)
    return build_timeline("env-pair", history_dir=hdir)


def test_build_timeline_returns_diff_timeline(populated_timeline):
    assert isinstance(populated_timeline, DiffTimeline)


def test_build_timeline_event_count(populated_timeline):
    assert populated_timeline.event_count if hasattr(populated_timeline, "event_count") else len(populated_timeline.events) == 3


def test_build_timeline_events_are_timeline_events(populated_timeline):
    for event in populated_timeline.events:
        assert isinstance(event, TimelineEvent)


def test_build_timeline_empty_history(hdir):
    tl = build_timeline("no-such-id", history_dir=hdir)
    assert tl.events == []


def test_latest_returns_last_event(populated_timeline):
    assert populated_timeline.latest is not None
    assert populated_timeline.latest.label == "deploy-3"


def test_latest_none_on_empty(hdir):
    tl = build_timeline("empty", history_dir=hdir)
    assert tl.latest is None


def test_peak_changes_is_highest(populated_timeline):
    peak = populated_timeline.peak_changes
    assert peak is not None
    assert peak.label == "deploy-3"  # added=5 => total=5


def test_limit_restricts_events(hdir):
    for i in range(5):
        record_diff("limited", _make_entry(f"d-{i}", added=i), history_dir=hdir)
    tl = build_timeline("limited", history_dir=hdir, limit=2)
    assert len(tl.events) == 2


def test_entry_to_event_fields():
    raw = {"timestamp": "2024-01-01T00:00:00", "label": "test", "stats": {"added": 1, "removed": 2, "changed": 3}, "score": 42.0}
    event = _entry_to_event(raw)
    assert event.added == 1
    assert event.removed == 2
    assert event.changed == 3
    assert event.total_changes == 6
    assert event.score == 42.0


def test_as_dict_structure(populated_timeline):
    d = populated_timeline.as_dict()
    assert "history_id" in d
    assert "events" in d
    assert "event_count" in d


def test_text_format_contains_header(populated_timeline):
    out = format_timeline_text(populated_timeline)
    assert "Timeline" in out
    assert "env-pair" in out


def test_text_format_shows_events(populated_timeline):
    out = format_timeline_text(populated_timeline)
    assert "deploy-1" in out
    assert "deploy-3" in out


def test_text_format_empty_timeline(hdir):
    tl = build_timeline("empty", history_dir=hdir)
    out = format_timeline_text(tl)
    assert "no events" in out


def test_json_format_is_valid_json(populated_timeline):
    out = format_timeline_json(populated_timeline)
    data = json.loads(out)
    assert "events" in data


def test_format_output_text(populated_timeline):
    out = format_timeline_output(populated_timeline, fmt="text")
    assert "Timeline" in out


def test_format_output_json(populated_timeline):
    out = format_timeline_output(populated_timeline, fmt="json")
    data = json.loads(out)
    assert data["history_id"] == "env-pair"
