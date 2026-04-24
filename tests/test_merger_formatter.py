"""Tests for stackdiff.merger_formatter."""
import json

import pytest

from stackdiff.diff_engine import DiffResult
from stackdiff.diff_merger import merge_diffs
from stackdiff.merger_formatter import (
    format_merged_json,
    format_merged_output,
    format_merged_text,
)


@pytest.fixture()
def merged():
    dr1 = DiffResult(
        removed={"db.host": "old"},
        added={"new.key": "val"},
        changed={"app.port": ("8080", "9090")},
    )
    dr2 = DiffResult(
        removed={},
        added={"new.key": "other"},
        changed={},
    )
    return merge_diffs([("staging", dr1), ("prod", dr2)])


@pytest.fixture()
def empty_merged():
    dr = DiffResult(removed={}, added={}, changed={})
    return merge_diffs([("a", dr), ("b", dr)])


def test_text_format_contains_header(merged):
    out = format_merged_text(merged)
    assert "Merged Diff" in out


def test_text_format_shows_labels(merged):
    out = format_merged_text(merged)
    assert "staging" in out
    assert "prod" in out


def test_text_format_shows_key(merged):
    out = format_merged_text(merged)
    assert "db.host" in out
    assert "app.port" in out


def test_text_format_empty_shows_no_diff(empty_merged):
    out = format_merged_text(empty_merged)
    assert "no differences" in out


def test_json_format_is_valid_json(merged):
    out = format_merged_json(merged)
    data = json.loads(out)
    assert "labels" in data
    assert "keys" in data


def test_json_format_labels_correct(merged):
    data = json.loads(format_merged_json(merged))
    assert data["labels"] == ["staging", "prod"]


def test_json_format_keys_present(merged):
    data = json.loads(format_merged_json(merged))
    assert "db.host" in data["keys"]
    assert "new.key" in data["keys"]


def test_format_output_text(merged):
    out = format_merged_output(merged, fmt="text")
    assert "Merged Diff" in out


def test_format_output_json(merged):
    out = format_merged_output(merged, fmt="json")
    assert json.loads(out)["labels"] == ["staging", "prod"]
