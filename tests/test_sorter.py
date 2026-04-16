"""Tests for stackdiff.sorter."""
import pytest
from stackdiff.sorter import sort_flat_config, sort_diff_result, SORT_KEY, SORT_STATUS, SORT_NONE
from stackdiff.diff_engine import DiffResult


@pytest.fixture()
def unsorted_cfg():
    return {"zebra": "1", "apple": "2", "mango": "3"}


@pytest.fixture()
def mixed_diff():
    return DiffResult(
        diffs={
            "zoo": {"status": "unchanged", "value_a": "1", "value_b": "1"},
            "alpha": {"status": "added", "value_a": None, "value_b": "new"},
            "beta": {"status": "removed", "value_a": "old", "value_b": None},
            "gamma": {"status": "changed", "value_a": "x", "value_b": "y"},
        },
        label_a="staging",
        label_b="production",
    )


def test_sort_flat_config_alphabetical(unsorted_cfg):
    result = sort_flat_config(unsorted_cfg)
    assert list(result.keys()) == ["apple", "mango", "zebra"]


def test_sort_flat_config_reverse(unsorted_cfg):
    result = sort_flat_config(unsorted_cfg, reverse=True)
    assert list(result.keys()) == ["zebra", "mango", "apple"]


def test_sort_flat_config_does_not_mutate(unsorted_cfg):
    original_keys = list(unsorted_cfg.keys())
    sort_flat_config(unsorted_cfg)
    assert list(unsorted_cfg.keys()) == original_keys


def test_sort_diff_by_key(mixed_diff):
    result = sort_diff_result(mixed_diff, mode=SORT_KEY)
    assert list(result.diffs.keys()) == ["alpha", "beta", "gamma", "zoo"]


def test_sort_diff_by_status(mixed_diff):
    result = sort_diff_result(mixed_diff, mode=SORT_STATUS)
    statuses = [v["status"] for v in result.diffs.values()]
    assert statuses[0] == "removed"
    assert statuses[1] == "added"
    assert statuses[2] == "changed"
    assert statuses[3] == "unchanged"


def test_sort_diff_none_preserves_order(mixed_diff):
    original_keys = list(mixed_diff.diffs.keys())
    result = sort_diff_result(mixed_diff, mode=SORT_NONE)
    assert list(result.diffs.keys()) == original_keys


def test_sort_diff_invalid_mode_raises(mixed_diff):
    with pytest.raises(ValueError, match="Invalid sort mode"):
        sort_diff_result(mixed_diff, mode="bogus")


def test_sort_diff_preserves_labels(mixed_diff):
    result = sort_diff_result(mixed_diff, mode=SORT_KEY)
    assert result.label_a == "staging"
    assert result.label_b == "production"
