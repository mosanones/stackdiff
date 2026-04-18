"""Tests for stackdiff.audit_log."""
import json
from pathlib import Path

import pytest

from stackdiff.audit_log import (
    AuditEntry,
    load_entries,
    make_entry,
    record_entry,
)


@pytest.fixture
def log_dir(tmp_path):
    return tmp_path / "audit"


@pytest.fixture
def entry():
    return make_entry(
        operation="diff",
        source_a="staging.yaml",
        source_b="prod.yaml",
        score_label="moderate",
        total_changes=4,
        critical_count=1,
        tags=["scheduled"],
    )


def test_make_entry_fields(entry):
    assert entry.operation == "diff"
    assert entry.source_a == "staging.yaml"
    assert entry.score_label == "moderate"
    assert entry.total_changes == 4
    assert "scheduled" in entry.tags


def test_make_entry_has_timestamp(entry):
    assert entry.timestamp
    assert "T" in entry.timestamp  # ISO format


def test_as_dict_keys(entry):
    d = entry.as_dict()
    for key in ("timestamp", "operation", "source_a", "source_b",
                "score_label", "total_changes", "critical_count", "tags"):
        assert key in d


def test_record_creates_file(entry, log_dir):
    path = record_entry(entry, log_dir=log_dir)
    assert path.exists()


def test_record_appends_jsonl(entry, log_dir):
    record_entry(entry, log_dir=log_dir)
    record_entry(entry, log_dir=log_dir)
    lines = (log_dir / "audit.jsonl").read_text().strip().splitlines()
    assert len(lines) == 2
    data = json.loads(lines[0])
    assert data["operation"] == "diff"


def test_load_entries_empty(log_dir):
    result = load_entries(log_dir=log_dir)
    assert result == []


def test_load_entries_returns_audit_entries(entry, log_dir):
    record_entry(entry, log_dir=log_dir)
    entries = load_entries(log_dir=log_dir)
    assert len(entries) == 1
    assert isinstance(entries[0], AuditEntry)
    assert entries[0].source_b == "prod.yaml"


def test_load_entries_multiple(log_dir):
    for op in ("diff", "snapshot", "baseline"):
        e = make_entry(op, "a", "b")
        record_entry(e, log_dir=log_dir)
    entries = load_entries(log_dir=log_dir)
    assert len(entries) == 3
    ops = [e.operation for e in entries]
    assert "snapshot" in ops
