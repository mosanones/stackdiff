"""Tests for stackdiff.diff_history."""
import pytest
from pathlib import Path

from stackdiff.diff_history import (
    clear_history,
    list_histories,
    load_history,
    record_diff,
    _trim,
    MAX_ENTRIES,
)


@pytest.fixture()
def hdir(tmp_path: Path) -> Path:
    return tmp_path / "history"


def test_record_creates_file(hdir):
    path = record_diff("prod", {"added": {}, "removed": {}}, history_dir=hdir)
    assert path.exists()


def test_load_returns_entries(hdir):
    record_diff("prod", {"added": {"KEY": "val"}, "removed": {}}, history_dir=hdir)
    record_diff("prod", {"added": {}, "removed": {"OLD": "x"}}, history_dir=hdir)
    entries = load_history("prod", history_dir=hdir)
    assert len(entries) == 2
    assert "timestamp" in entries[0]
    assert "result" in entries[0]


def test_load_missing_returns_empty(hdir):
    assert load_history("nonexistent", history_dir=hdir) == []


def test_clear_removes_file(hdir):
    record_diff("staging", {}, history_dir=hdir)
    deleted = clear_history("staging", history_dir=hdir)
    assert deleted is True
    assert load_history("staging", history_dir=hdir) == []


def test_clear_missing_returns_false(hdir):
    assert clear_history("ghost", history_dir=hdir) is False


def test_list_histories(hdir):
    record_diff("alpha", {}, history_dir=hdir)
    record_diff("beta", {}, history_dir=hdir)
    names = list_histories(hdir)
    assert set(names) == {"alpha", "beta"}


def test_list_histories_empty_dir(hdir):
    assert list_histories(hdir) == []


def test_trim_caps_entries(hdir):
    for i in range(MAX_ENTRIES + 10):
        record_diff("big", {"i": i}, history_dir=hdir)
    entries = load_history("big", history_dir=hdir)
    assert len(entries) == MAX_ENTRIES


def test_entries_ordered_oldest_first(hdir):
    for i in range(3):
        record_diff("ordered", {"seq": i}, history_dir=hdir)
    entries = load_history("ordered", history_dir=hdir)
    seqs = [e["result"]["seq"] for e in entries]
    assert seqs == [0, 1, 2]
