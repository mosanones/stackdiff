import json
import pytest
from stackdiff.diff_engine import DiffResult
from stackdiff.annotator import annotate_diff
from stackdiff.annotation_formatter import (
    format_annotated_text,
    format_annotated_json,
    format_annotated_output,
)


@pytest.fixture
def annotated():
    diff = DiffResult(
        removed={"db_password": "old_pass"},
        added={"new_host": "prod.example.com"},
        changed={"max_retries": ("3", "5")},
    )
    return annotate_diff(diff, extra_notes={"max_retries": "tuned for prod"})


@pytest.fixture
def empty_annotated():
    diff = DiffResult(removed={}, added={}, changed={})
    return annotate_diff(diff)


def test_text_format_contains_header(annotated):
    out = format_annotated_text(annotated)
    assert "Annotated diff" in out


def test_text_format_shows_removed(annotated):
    out = format_annotated_text(annotated)
    assert "db_password" in out
    assert "removed" in out


def test_text_format_shows_added(annotated):
    out = format_annotated_text(annotated)
    assert "new_host" in out
    assert "added" in out


def test_text_format_shows_changed_with_note(annotated):
    out = format_annotated_text(annotated)
    assert "max_retries" in out
    assert "tuned for prod" in out


def test_text_format_shows_total(annotated):
    out = format_annotated_text(annotated)
    assert "Total changes: 3" in out


def test_text_format_no_diff(empty_annotated):
    out = format_annotated_text(empty_annotated)
    assert "No differences" in out


def test_json_format_is_valid_json(annotated):
    out = format_annotated_json(annotated)
    data = json.loads(out)
    assert "annotations" in data
    assert data["total"] == 3


def test_json_format_contains_severity(annotated):
    out = format_annotated_json(annotated)
    data = json.loads(out)
    keys = {a["key"] for a in data["annotations"]}
    assert "db_password" in keys


def test_format_output_dispatches_json(annotated):
    out = format_annotated_output(annotated, fmt="json")
    data = json.loads(out)
    assert "annotations" in data


def test_format_output_dispatches_text(annotated):
    out = format_annotated_output(annotated, fmt="text", label_a="staging", label_b="prod")
    assert "staging" in out
    assert "prod" in out
