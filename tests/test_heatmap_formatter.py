"""Tests for stackdiff.heatmap_formatter."""
from __future__ import annotations

import json

import pytest

from stackdiff.diff_engine import DiffResult
from stackdiff.diff_heatmap import DiffHeatmap, HeatmapEntry, build_heatmap
from stackdiff.heatmap_formatter import (
    format_heatmap_json,
    format_heatmap_output,
    format_heatmap_text,
)


@pytest.fixture()
def heatmap() -> DiffHeatmap:
    drs = [
        DiffResult(
            label_a="s",
            label_b="p",
            removed={"db.host": "a"},
            added={"db.host": "b"},
            changed={"app.port": ("80", "443")},
        ),
        DiffResult(
            label_a="s",
            label_b="p",
            removed={},
            added={},
            changed={"app.port": ("443", "8080")},
        ),
    ]
    return build_heatmap(drs)


@pytest.fixture()
def empty_heatmap() -> DiffHeatmap:
    return DiffHeatmap(total_diffs=0, entries=[])


def test_text_format_contains_header(heatmap):
    out = format_heatmap_text(heatmap)
    assert "Heatmap" in out


def test_text_format_shows_hottest_key(heatmap):
    out = format_heatmap_text(heatmap)
    assert "app.port" in out


def test_text_format_shows_change_count(heatmap):
    out = format_heatmap_text(heatmap)
    assert "2x" in out


def test_text_format_shows_bar(heatmap):
    out = format_heatmap_text(heatmap)
    assert "[" in out and "]" in out


def test_text_format_empty_heatmap(empty_heatmap):
    out = format_heatmap_text(empty_heatmap)
    assert "no changes" in out.lower()


def test_json_format_is_valid_json(heatmap):
    out = format_heatmap_json(heatmap)
    parsed = json.loads(out)
    assert "total_diffs" in parsed
    assert "entries" in parsed


def test_json_entries_have_expected_keys(heatmap):
    out = format_heatmap_json(heatmap)
    entries = json.loads(out)["entries"]
    for e in entries:
        assert "key" in e
        assert "change_count" in e
        assert "frequency" in e


def test_format_output_text(heatmap):
    assert format_heatmap_output(heatmap, fmt="text") == format_heatmap_text(heatmap)


def test_format_output_json(heatmap):
    assert format_heatmap_output(heatmap, fmt="json") == format_heatmap_json(heatmap)


def test_format_output_defaults_to_text(heatmap):
    assert format_heatmap_output(heatmap) == format_heatmap_text(heatmap)
