"""Tests for stackdiff.formatter."""
import json
import pytest
from stackdiff.diff_engine import DiffResult
from stackdiff.formatter import format_text, format_json, format_output


@pytest.fixture
def no_diff_result():
    flat = {"DB_HOST": "localhost", "PORT": "5432"}
    return DiffResult(left=flat, right=flat, left_label="staging", right_label="prod")


@pytest.fixture
def diff_result():
    left = {"DB_HOST": "staging-db", "PORT": "5432", "DEBUG": "true"}
    right = {"DB_HOST": "prod-db", "PORT": "5432", "LOG_LEVEL": "warn"}
    return DiffResult(left=left, right=right, left_label="staging", right_label="prod")


def test_format_text_no_diff(no_diff_result):
    output = format_text(no_diff_result, color=False)
    assert "No differences" in output


def test_format_text_shows_labels(diff_result):
    output = format_text(diff_result, color=False)
    assert "staging" in output
    assert "prod" in output


def test_format_text_shows_removed_key(diff_result):
    output = format_text(diff_result, color=False)
    assert "- DEBUG" in output


def test_format_text_shows_added_key(diff_result):
    output = format_text(diff_result, color=False)
    assert "+ LOG_LEVEL" in output


def test_format_text_shows_changed_key(diff_result):
    output = format_text(diff_result, color=False)
    assert "~ DB_HOST" in output
    assert "staging-db" in output
    assert "prod-db" in output


def test_format_json_structure(diff_result):
    raw = format_json(diff_result)
    data = json.loads(raw)
    assert data["left_label"] == "staging"
    assert data["right_label"] == "prod"
    assert "DB_HOST" in data["changed"]
    assert "DEBUG" in data["only_in_left"]
    assert "LOG_LEVEL" in data["only_in_right"]


def test_format_output_dispatches_json(diff_result):
    output = format_output(diff_result, fmt="json")
    data = json.loads(output)
    assert "changed" in data


def test_format_output_dispatches_text(diff_result):
    output = format_output(diff_result, fmt="text", color=False)
    assert "Diff:" in output
