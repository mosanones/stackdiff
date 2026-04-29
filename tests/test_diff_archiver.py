"""Tests for stackdiff.diff_archiver."""
from __future__ import annotations

import pytest

from stackdiff.diff_archiver import (
    ArchiveEntry,
    delete_archive,
    list_archives,
    load_archive,
    save_archive,
)


@pytest.fixture()
def arc_dir(tmp_path):
    return tmp_path / "archive"


@pytest.fixture()
def sample_report():
    return {"score": 42, "label": "moderate", "changes": 3}


def test_save_creates_file(arc_dir, sample_report):
    entry = save_archive(sample_report, label="staging", archive_dir=arc_dir)
    assert (arc_dir / f"{entry.archive_id}.json").exists()


def test_save_returns_archive_entry(arc_dir, sample_report):
    entry = save_archive(sample_report, label="prod", archive_dir=arc_dir)
    assert isinstance(entry, ArchiveEntry)
    assert entry.label == "prod"
    assert entry.report == sample_report


def test_load_returns_entry(arc_dir, sample_report):
    saved = save_archive(sample_report, label="staging", archive_dir=arc_dir)
    loaded = load_archive(saved.archive_id, archive_dir=arc_dir)
    assert loaded.archive_id == saved.archive_id
    assert loaded.report == sample_report


def test_load_missing_raises(arc_dir):
    with pytest.raises(FileNotFoundError):
        load_archive("nonexistent_id", archive_dir=arc_dir)


def test_list_archives_empty(arc_dir):
    result = list_archives(archive_dir=arc_dir)
    assert result == []


def test_list_archives_returns_ids(arc_dir, sample_report):
    e1 = save_archive(sample_report, label="a", archive_dir=arc_dir)
    e2 = save_archive(sample_report, label="b", archive_dir=arc_dir)
    ids = list_archives(archive_dir=arc_dir)
    assert e1.archive_id in ids
    assert e2.archive_id in ids


def test_list_archives_filter_by_label(arc_dir, sample_report):
    save_archive(sample_report, label="staging", archive_dir=arc_dir)
    save_archive(sample_report, label="prod", archive_dir=arc_dir)
    ids = list_archives(archive_dir=arc_dir, label="staging")
    assert all(i.startswith("staging") for i in ids)


def test_delete_removes_file(arc_dir, sample_report):
    entry = save_archive(sample_report, label="tmp", archive_dir=arc_dir)
    delete_archive(entry.archive_id, archive_dir=arc_dir)
    assert entry.archive_id not in list_archives(archive_dir=arc_dir)


def test_delete_missing_raises(arc_dir):
    with pytest.raises(FileNotFoundError):
        delete_archive("ghost_entry", archive_dir=arc_dir)


def test_as_dict_structure(arc_dir, sample_report):
    entry = save_archive(sample_report, label="check", archive_dir=arc_dir)
    d = entry.as_dict()
    assert set(d.keys()) == {"archive_id", "label", "timestamp", "report"}
    assert d["label"] == "check"
    assert d["report"] == sample_report


def test_save_multiple_same_label(arc_dir, sample_report):
    """Saving multiple archives with the same label should produce distinct IDs."""
    e1 = save_archive(sample_report, label="dup", archive_dir=arc_dir)
    e2 = save_archive(sample_report, label="dup", archive_dir=arc_dir)
    assert e1.archive_id != e2.archive_id
    ids = list_archives(archive_dir=arc_dir, label="dup")
    assert len(ids) == 2
