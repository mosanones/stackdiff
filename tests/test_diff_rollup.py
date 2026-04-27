"""Tests for stackdiff.diff_rollup."""
import pytest
from stackdiff.diff_engine import DiffResult
from stackdiff.diff_rollup import RollupEntry, RollupReport, build_rollup


@pytest.fixture
def dr_clean():
    return DiffResult(
        added={},
        removed={},
        changed={},
        left_label="staging",
        right_label="prod",
    )


@pytest.fixture
def dr_small():
    return DiffResult(
        added={"new_key": "val"},
        removed={"old_key": "old"},
        changed={"host": ("a", "b")},
        left_label="staging",
        right_label="prod",
    )


@pytest.fixture
def dr_large():
    return DiffResult(
        added={"k1": "v1", "k2": "v2"},
        removed={"r1": "x", "r2": "y", "r3": "z"},
        changed={"c1": ("a", "b"), "c2": ("c", "d")},
        left_label="staging",
        right_label="prod",
    )


def test_build_rollup_returns_rollup_report(dr_clean):
    report = build_rollup([("env-a", dr_clean)])
    assert isinstance(report, RollupReport)


def test_build_rollup_empty_input():
    report = build_rollup([])
    assert report.entries == []
    assert report.total_changes == 0
    assert report.most_changed is None


def test_rollup_entry_counts(dr_small):
    report = build_rollup([("env-a", dr_small)])
    entry = report.entries[0]
    assert entry.added == 1
    assert entry.removed == 1
    assert entry.changed == 1
    assert entry.total == 3


def test_rollup_entry_label(dr_small):
    report = build_rollup([("my-env", dr_small)])
    assert report.entries[0].label == "my-env"


def test_total_changes_across_entries(dr_small, dr_large):
    report = build_rollup([("a", dr_small), ("b", dr_large)])
    # dr_small: 3, dr_large: 2+3+2=7
    assert report.total_changes == 10


def test_most_changed_returns_highest(dr_small, dr_large):
    report = build_rollup([("small", dr_small), ("large", dr_large)])
    assert report.most_changed is not None
    assert report.most_changed.label == "large"


def test_most_changed_single_entry(dr_small):
    report = build_rollup([("only", dr_small)])
    assert report.most_changed.label == "only"


def test_clean_entry_has_zero_total(dr_clean):
    report = build_rollup([("clean", dr_clean)])
    assert report.entries[0].total == 0


def test_as_dict_structure(dr_small):
    report = build_rollup([("env", dr_small)])
    d = report.as_dict()
    assert "entries" in d
    assert "total_changes" in d
    assert "most_changed" in d
    assert d["most_changed"] == "env"


def test_entry_as_dict_keys(dr_small):
    report = build_rollup([("env", dr_small)])
    entry_dict = report.entries[0].as_dict()
    assert set(entry_dict.keys()) == {"label", "added", "removed", "changed", "total"}
