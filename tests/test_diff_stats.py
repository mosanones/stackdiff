"""Tests for stackdiff.diff_stats."""
import pytest
from stackdiff.diff_engine import DiffResult
from stackdiff.diff_stats import compute_stats, DiffStats


@pytest.fixture
def empty_diff():
    return DiffResult(added={}, removed={}, changed={}, unchanged={})


@pytest.fixture
def simple_diff():
    return DiffResult(
        added={"db.host": "prod-db"},
        removed={"db.port": "5433"},
        changed={"app.debug": ("true", "false")},
        unchanged={"app.name": "myapp", "app.version": "1.0"},
    )


def test_compute_stats_returns_diff_stats(simple_diff):
    result = compute_stats(simple_diff)
    assert isinstance(result, DiffStats)


def test_total_keys(simple_diff):
    stats = compute_stats(simple_diff)
    assert stats.total_keys == 5


def test_added_count(simple_diff):
    stats = compute_stats(simple_diff)
    assert stats.added == 1


def test_removed_count(simple_diff):
    stats = compute_stats(simple_diff)
    assert stats.removed == 1


def test_changed_count(simple_diff):
    stats = compute_stats(simple_diff)
    assert stats.changed == 1


def test_unchanged_count(simple_diff):
    stats = compute_stats(simple_diff)
    assert stats.unchanged == 2


def test_change_rate(simple_diff):
    stats = compute_stats(simple_diff)
    assert abs(stats.change_rate - 3 / 5) < 1e-6


def test_empty_diff_zero_rate(empty_diff):
    stats = compute_stats(empty_diff)
    assert stats.change_rate == 0.0
    assert stats.total_keys == 0


def test_as_dict_keys(simple_diff):
    d = compute_stats(simple_diff).as_dict()
    assert set(d.keys()) == {"total_keys", "added", "removed", "changed", "unchanged", "change_rate"}


def test_change_rate_rounded(simple_diff):
    stats = compute_stats(simple_diff)
    assert stats.change_rate == round(stats.change_rate, 4)
