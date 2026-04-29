"""Tests for stackdiff.archiver_cli."""
from __future__ import annotations

import json

import pytest

from stackdiff.diff_archiver import save_archive
from stackdiff.archiver_cli import build_archiver_parser, main


@pytest.fixture()
def arc_dir(tmp_path):
    return tmp_path / "archive"


@pytest.fixture()
def saved_entry(arc_dir):
    return save_archive({"score": 10, "changes": 1}, label="test", archive_dir=arc_dir)


def test_build_archiver_parser_returns_parser(arc_dir):
    parser = build_archiver_parser()
    assert parser is not None


def test_list_empty(arc_dir, capsys):
    rc = main(["--archive-dir", str(arc_dir), "list"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "No archives found" in out


def test_list_shows_entry(arc_dir, saved_entry, capsys):
    rc = main(["--archive-dir", str(arc_dir), "list"])
    out = capsys.readouterr().out
    assert rc == 0
    assert saved_entry.archive_id in out


def test_list_json_output(arc_dir, saved_entry, capsys):
    rc = main(["--archive-dir", str(arc_dir), "list", "--json"])
    out = capsys.readouterr().out
    assert rc == 0
    ids = json.loads(out)
    assert isinstance(ids, list)
    assert saved_entry.archive_id in ids


def test_list_filter_by_label(arc_dir, capsys):
    save_archive({}, label="staging", archive_dir=arc_dir)
    save_archive({}, label="prod", archive_dir=arc_dir)
    rc = main(["--archive-dir", str(arc_dir), "list", "--label", "staging"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "staging" in out
    assert "prod" not in out


def test_show_entry(arc_dir, saved_entry, capsys):
    rc = main(["--archive-dir", str(arc_dir), "show", saved_entry.archive_id])
    out = capsys.readouterr().out
    assert rc == 0
    assert saved_entry.archive_id in out
    assert "test" in out


def test_show_json_output(arc_dir, saved_entry, capsys):
    rc = main(["--archive-dir", str(arc_dir), "show", saved_entry.archive_id, "--json"])
    out = capsys.readouterr().out
    assert rc == 0
    data = json.loads(out)
    assert data["archive_id"] == saved_entry.archive_id


def test_show_missing_returns_one(arc_dir, capsys):
    rc = main(["--archive-dir", str(arc_dir), "show", "no_such_id"])
    assert rc == 1


def test_delete_entry(arc_dir, saved_entry, capsys):
    rc = main(["--archive-dir", str(arc_dir), "delete", saved_entry.archive_id])
    out = capsys.readouterr().out
    assert rc == 0
    assert "Deleted" in out


def test_delete_missing_returns_one(arc_dir, capsys):
    rc = main(["--archive-dir", str(arc_dir), "delete", "ghost"])
    assert rc == 1
