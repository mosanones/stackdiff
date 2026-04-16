"""Tests for stackdiff.exporter."""
import pytest

from stackdiff.diff_engine import DiffResult
from stackdiff.exporter import export, to_csv, to_markdown


@pytest.fixture()
def sample_diff() -> DiffResult:
    return DiffResult(
        removed={"DB_HOST": "localhost"},
        added={"NEW_RELIC_KEY": "abc123"},
        changed={"LOG_LEVEL": ("DEBUG", "WARNING")},
    )


@pytest.fixture()
def empty_diff() -> DiffResult:
    return DiffResult(removed={}, added={}, changed={})


# --- CSV ---

def test_csv_header(sample_diff):
    csv = to_csv(sample_diff)
    assert csv.startswith("key,status,staging,production")


def test_csv_removed_row(sample_diff):
    csv = to_csv(sample_diff)
    assert "DB_HOST,removed,localhost," in csv


def test_csv_added_row(sample_diff):
    csv = to_csv(sample_diff)
    assert "NEW_RELIC_KEY,added,,abc123" in csv


def test_csv_changed_row(sample_diff):
    csv = to_csv(sample_diff)
    assert "LOG_LEVEL,changed,DEBUG,WARNING" in csv


def test_csv_custom_labels(sample_diff):
    csv = to_csv(sample_diff, label_a="dev", label_b="prod")
    assert csv.startswith("key,status,dev,prod")


def test_csv_empty_diff(empty_diff):
    csv = to_csv(empty_diff)
    lines = [l for l in csv.splitlines() if l]
    assert len(lines) == 1  # header only


# --- Markdown ---

def test_markdown_contains_header(sample_diff):
    md = to_markdown(sample_diff)
    assert "| key | status |" in md


def test_markdown_removed_row(sample_diff):
    md = to_markdown(sample_diff)
    assert "removed" in md and "DB_HOST" in md


def test_markdown_changed_row(sample_diff):
    md = to_markdown(sample_diff)
    assert "LOG_LEVEL" in md and "DEBUG" in md and "WARNING" in md


# --- export() dispatcher ---

def test_export_csv(sample_diff):
    result = export(sample_diff, fmt="csv")
    assert "key,status" in result


def test_export_markdown(sample_diff):
    result = export(sample_diff, fmt="markdown")
    assert "| key | status |" in result


def test_export_md_alias(sample_diff):
    result = export(sample_diff, fmt="md")
    assert "| key | status |" in result


def test_export_invalid_format(sample_diff):
    with pytest.raises(ValueError, match="Unsupported export format"):
        export(sample_diff, fmt="xml")


def test_export_writes_file(tmp_path, sample_diff):
    out = tmp_path / "diff.csv"
    export(sample_diff, fmt="csv", path=str(out))
    assert out.exists()
    assert "LOG_LEVEL" in out.read_text()
