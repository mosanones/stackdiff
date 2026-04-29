"""Tests for stackdiff.diff_deduplicator."""

import pytest
from stackdiff.diff_engine import DiffResult
from stackdiff.diff_deduplicator import (
    DeduplicatedKey,
    DeduplicatedDiff,
    deduplicate_diffs,
)


@pytest.fixture
def dr_stable():
    """DiffResult where 'db.host' changed every run."""
    return DiffResult(
        removed={"db.host": "old-host"},
        added={"db.host": "new-host"},
    )


@pytest.fixture
def dr_flap():
    """DiffResult where 'app.debug' appears only once."""
    return DiffResult(
        removed={"app.debug": "false"},
        added={"app.debug": "true"},
    )


@pytest.fixture
def dr_empty():
    return DiffResult(removed={}, added={})


# --- DeduplicatedKey ---

def test_as_dict_keys():
    key = DeduplicatedKey(key="x", occurrences=3, total_runs=5, last_removed="a", last_added="b")
    d = key.as_dict()
    assert set(d.keys()) == {"key", "occurrences", "total_runs", "frequency", "last_removed", "last_added"}


def test_is_stable_when_all_runs_changed():
    key = DeduplicatedKey(key="x", occurrences=4, total_runs=4, last_removed=None, last_added=None)
    assert key.is_stable is True


def test_is_not_stable_when_partial():
    key = DeduplicatedKey(key="x", occurrences=2, total_runs=4, last_removed=None, last_added=None)
    assert key.is_stable is False


def test_is_flapping_below_half():
    key = DeduplicatedKey(key="x", occurrences=1, total_runs=4, last_removed=None, last_added=None)
    assert key.is_flapping is True


def test_is_not_flapping_above_half():
    key = DeduplicatedKey(key="x", occurrences=3, total_runs=4, last_removed=None, last_added=None)
    assert key.is_flapping is False


def test_frequency_calculation():
    key = DeduplicatedKey(key="x", occurrences=1, total_runs=4, last_removed=None, last_added=None)
    assert key.as_dict()["frequency"] == 0.25


# --- deduplicate_diffs ---

def test_deduplicate_returns_deduped_diff(dr_stable):
    result = deduplicate_diffs([dr_stable, dr_stable])
    assert isinstance(result, DeduplicatedDiff)


def test_total_runs_recorded(dr_stable):
    result = deduplicate_diffs([dr_stable, dr_stable, dr_stable])
    assert result.total_runs == 3


def test_stable_key_detected(dr_stable):
    result = deduplicate_diffs([dr_stable, dr_stable])
    stable = result.stable_keys()
    assert any(k.key == "db.host" for k in stable)


def test_flapping_key_detected(dr_stable, dr_flap, dr_empty):
    # app.debug only appears in 1 of 3 runs
    result = deduplicate_diffs([dr_stable, dr_flap, dr_empty])
    flapping = result.flapping_keys()
    assert any(k.key == "app.debug" for k in flapping)


def test_empty_runs_returns_empty_diff():
    result = deduplicate_diffs([])
    assert result.total_runs == 0
    assert result.keys == []


def test_as_dict_structure(dr_stable):
    result = deduplicate_diffs([dr_stable])
    d = result.as_dict()
    assert "total_runs" in d
    assert "unique_changed_keys" in d
    assert "stable_keys" in d
    assert "flapping_keys" in d
    assert isinstance(d["keys"], list)


def test_keys_sorted_by_occurrence_descending(dr_stable, dr_flap):
    # db.host appears in both runs, app.debug in only one
    result = deduplicate_diffs([dr_stable, dr_stable, dr_flap])
    assert result.keys[0].key == "db.host"


def test_last_removed_and_added_tracked(dr_stable):
    result = deduplicate_diffs([dr_stable])
    key = next(k for k in result.keys if k.key == "db.host")
    assert key.last_removed == "old-host"
    assert key.last_added == "new-host"
