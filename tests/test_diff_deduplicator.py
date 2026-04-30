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


def test_frequency_is_one_when_all_runs():
    """Frequency should be exactly 1.0 when occurrences equals total_runs."""
    key = DeduplicatedKey(key="x", occurrences=5, total_runs=5, last_removed=None, last_added=None)
    assert key.as_dict()["frequency"] == 1.0


def test_frequency_is_zero_for_single_run_out_of_many():
    """Frequency rounds correctly for a single occurrence across many runs."""
    key = DeduplicatedKey(key="x", occurrences=1, total_runs=10, last_removed=None, last_added=None)
    assert key.as_dict()["frequency"] == 0.1


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


def test_stable_key_not_in_flapping(dr_stable):
    """A key that changes every run should not appear in flapping_keys."""
    result = deduplicate_diffs([dr_stable, dr_stable, dr_stable])
    flapping = result.flapping_keys()
    assert not any(k.key == "db.host" for k in flapping)


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
