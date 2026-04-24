"""Tests for stackdiff.diff_merger."""
import pytest

from stackdiff.diff_engine import DiffResult
from stackdiff.diff_merger import MergedDiff, merge_diffs


@pytest.fixture()
def dr_staging() -> DiffResult:
    return DiffResult(
        removed={"db.host": "old-db"},
        added={"cache.url": "redis://new"},
        changed={"app.debug": ("true", "false")},
    )


@pytest.fixture()
def dr_prod() -> DiffResult:
    return DiffResult(
        removed={},
        added={"cache.url": "redis://prod"},
        changed={"app.debug": ("true", "false")},
    )


@pytest.fixture()
def dr_empty() -> DiffResult:
    return DiffResult(removed={}, added={}, changed={})


def test_merge_diffs_returns_merged_diff(dr_staging, dr_prod):
    result = merge_diffs([("staging", dr_staging), ("prod", dr_prod)])
    assert isinstance(result, MergedDiff)


def test_labels_preserved(dr_staging, dr_prod):
    result = merge_diffs([("staging", dr_staging), ("prod", dr_prod)])
    assert result.labels == ["staging", "prod"]


def test_all_keys_union(dr_staging, dr_prod):
    result = merge_diffs([("staging", dr_staging), ("prod", dr_prod)])
    assert "db.host" in result.all_keys()
    assert "cache.url" in result.all_keys()
    assert "app.debug" in result.all_keys()


def test_absent_key_recorded_as_none(dr_staging, dr_prod):
    result = merge_diffs([("staging", dr_staging), ("prod", dr_prod)])
    # db.host only in staging
    entries = result.merged["db.host"]
    assert entries[0] == ("old-db", None)  # staging: removed
    assert entries[1] is None             # prod: not present


def test_changed_key_recorded_correctly(dr_staging, dr_prod):
    result = merge_diffs([("staging", dr_staging), ("prod", dr_prod)])
    entries = result.merged["app.debug"]
    assert entries[0] == ("true", "false")
    assert entries[1] == ("true", "false")


def test_keys_changed_in_all(dr_staging, dr_prod):
    result = merge_diffs([("staging", dr_staging), ("prod", dr_prod)])
    changed_all = result.keys_changed_in_all()
    assert "app.debug" in changed_all
    assert "db.host" not in changed_all  # absent in prod


def test_empty_diffs_produce_empty_merged(dr_empty):
    result = merge_diffs([("a", dr_empty), ("b", dr_empty)])
    assert result.all_keys() == []


def test_single_pair(dr_staging):
    result = merge_diffs([("only", dr_staging)])
    assert result.labels == ["only"]
    assert "db.host" in result.all_keys()


def test_as_dict_structure(dr_staging, dr_prod):
    result = merge_diffs([("staging", dr_staging), ("prod", dr_prod)])
    d = result.as_dict()
    assert "labels" in d
    assert "merged" in d
