"""Tests for stackdiff.group_formatter."""
from __future__ import annotations

import json

import pytest

from stackdiff.diff_engine import DiffResult
from stackdiff.diff_grouper import group_by_namespace
from stackdiff.group_formatter import (
    format_grouped_json,
    format_grouped_output,
    format_grouped_text,
)


@pytest.fixture()
def grouped():
    diff = DiffResult(
        removed={"db.host": "old"},
        added={"db.port": "5433"},
        changed={"app.debug": ("true", "false")},
    )
    return group_by_namespace(diff)


@pytest.fixture()
def empty_grouped():
    diff = DiffResult(removed={}, added={}, changed={})
    return group_by_namespace(diff)


def test_text_format_contains_header(grouped):
    out = format_grouped_text(grouped)
    assert "Grouped diff" in out


def test_text_format_shows_group_name(grouped):
    out = format_grouped_text(grouped)
    assert "[db]" in out


def test_text_format_shows_key(grouped):
    out = format_grouped_text(grouped)
    assert "db.host" in out


def test_text_format_custom_labels(grouped):
    out = format_grouped_text(grouped, label_a="staging", label_b="production")
    assert "staging" in out
    assert "production" in out


def test_text_format_empty_diff_message(empty_grouped):
    out = format_grouped_text(empty_grouped)
    assert "No changes" in out


def test_json_format_is_valid_json(grouped):
    out = format_grouped_json(grouped)
    data = json.loads(out)
    assert "grouped_diff" in data


def test_json_format_labels(grouped):
    out = format_grouped_json(grouped, label_a="stg", label_b="prd")
    data = json.loads(out)
    assert data["labels"]["a"] == "stg"
    assert data["labels"]["b"] == "prd"


def test_json_format_contains_groups(grouped):
    out = format_grouped_json(grouped)
    data = json.loads(out)
    assert "groups" in data["grouped_diff"]


def test_format_output_text(grouped):
    out = format_grouped_output(grouped, fmt="text")
    assert "[db]" in out


def test_format_output_json(grouped):
    out = format_grouped_output(grouped, fmt="json")
    data = json.loads(out)
    assert "grouped_diff" in data
