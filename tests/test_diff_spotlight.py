"""Tests for diff_spotlight and spotlight_formatter."""
import json
import pytest

from stackdiff.diff_engine import DiffResult
from stackdiff.diff_spotlight import build_spotlight, DiffSpotlight, SpotlightEntry
from stackdiff.spotlight_formatter import (
    format_spotlight_text,
    format_spotlight_json,
    format_spotlight_output,
)


@pytest.fixture
def clean_diff():
    return DiffResult(removed={}, added={}, changed={})


@pytest.fixture
def secret_diff():
    return DiffResult(
        removed={"db.password": "old_secret"},
        added={"api_key": "new_key"},
        changed={"app.host": ("localhost", "prod.example.com")},
    )


# --- build_spotlight ---

def test_build_spotlight_returns_diff_spotlight(secret_diff):
    result = build_spotlight(secret_diff)
    assert isinstance(result, DiffSpotlight)


def test_build_spotlight_empty_diff_has_no_entries(clean_diff):
    result = build_spotlight(clean_diff)
    assert result.entries == []


def test_build_spotlight_entries_are_spotlight_entries(secret_diff):
    result = build_spotlight(secret_diff)
    for entry in result.entries:
        assert isinstance(entry, SpotlightEntry)


def test_build_spotlight_top_n_limits_results(secret_diff):
    result = build_spotlight(secret_diff, top_n=1)
    assert len(result.entries) <= 1


def test_build_spotlight_sorted_by_severity(secret_diff):
    result = build_spotlight(secret_diff)
    severities = [e.severity for e in result.entries]
    order = ["critical", "high", "medium", "low", "info"]
    ranked = [order.index(s) if s in order else 99 for s in severities]
    assert ranked == sorted(ranked)


def test_build_spotlight_total_score_is_numeric(secret_diff):
    result = build_spotlight(secret_diff)
    assert isinstance(result.total_score, (int, float))


def test_spotlight_top_returns_first_entry(secret_diff):
    result = build_spotlight(secret_diff)
    if result.entries:
        assert result.top is result.entries[0]


def test_spotlight_top_none_when_empty(clean_diff):
    result = build_spotlight(clean_diff)
    assert result.top is None


def test_spotlight_as_dict_keys(secret_diff):
    result = build_spotlight(secret_diff)
    d = result.as_dict()
    assert "total_score" in d
    assert "entries" in d


# --- formatters ---

def test_text_format_empty_spotlight(clean_diff):
    spotlight = build_spotlight(clean_diff)
    text = format_spotlight_text(spotlight)
    assert "no significant changes" in text


def test_text_format_contains_header(secret_diff):
    spotlight = build_spotlight(secret_diff)
    text = format_spotlight_text(spotlight)
    assert "Diff Spotlight" in text


def test_text_format_shows_key(secret_diff):
    spotlight = build_spotlight(secret_diff)
    text = format_spotlight_text(spotlight)
    keys = {e.key for e in spotlight.entries}
    for key in keys:
        assert key in text


def test_json_format_is_valid_json(secret_diff):
    spotlight = build_spotlight(secret_diff)
    raw = format_spotlight_json(spotlight)
    data = json.loads(raw)
    assert "entries" in data


def test_format_output_text(secret_diff):
    spotlight = build_spotlight(secret_diff)
    out = format_spotlight_output(spotlight, fmt="text")
    assert isinstance(out, str)


def test_format_output_json(secret_diff):
    spotlight = build_spotlight(secret_diff)
    out = format_spotlight_output(spotlight, fmt="json")
    json.loads(out)  # must not raise
