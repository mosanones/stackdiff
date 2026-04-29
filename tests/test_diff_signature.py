"""Tests for stackdiff.diff_signature."""
from __future__ import annotations

import pytest

from stackdiff.diff_engine import DiffResult
from stackdiff.diff_signature import (
    DiffSignature,
    sign_diff,
    signatures_match,
    _classify_keys,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def removed_diff() -> DiffResult:
    return DiffResult(
        left={"db.host": "old-host", "db.port": "5432"},
        right={"db.port": "5432"},
    )


@pytest.fixture
def added_diff() -> DiffResult:
    return DiffResult(
        left={"db.port": "5432"},
        right={"db.port": "5432", "db.host": "new-host"},
    )


@pytest.fixture
def changed_diff() -> DiffResult:
    return DiffResult(
        left={"api.url": "http://staging", "api.key": "abc"},
        right={"api.url": "http://prod", "api.key": "abc"},
    )


@pytest.fixture
def empty_diff() -> DiffResult:
    return DiffResult(left={}, right={})


# ---------------------------------------------------------------------------
# _classify_keys
# ---------------------------------------------------------------------------

def test_classify_keys_removed(removed_diff):
    removed, added, changed = _classify_keys(removed_diff)
    assert "db.host" in removed
    assert added == []
    assert changed == []


def test_classify_keys_added(added_diff):
    removed, added, changed = _classify_keys(added_diff)
    assert "db.host" in added
    assert removed == []
    assert changed == []


def test_classify_keys_changed(changed_diff):
    removed, added, changed = _classify_keys(changed_diff)
    assert "api.url" in changed
    assert removed == []
    assert added == []


# ---------------------------------------------------------------------------
# sign_diff
# ---------------------------------------------------------------------------

def test_sign_diff_returns_diff_signature(changed_diff):
    sig = sign_diff(changed_diff)
    assert isinstance(sig, DiffSignature)


def test_sign_diff_hexdigest_is_string(changed_diff):
    sig = sign_diff(changed_diff)
    assert isinstance(sig.hexdigest, str)
    assert len(sig.hexdigest) == 64  # sha256 default


def test_sign_diff_counts_match(removed_diff):
    sig = sign_diff(removed_diff)
    assert sig.removed_count == 1
    assert sig.added_count == 0
    assert sig.changed_count == 0


def test_sign_diff_key_count(changed_diff):
    sig = sign_diff(changed_diff)
    assert sig.key_count == 2


def test_sign_diff_empty_diff(empty_diff):
    sig = sign_diff(empty_diff)
    assert sig.key_count == 0
    assert sig.removed_count == 0
    assert sig.added_count == 0
    assert sig.changed_count == 0


def test_sign_diff_stable_across_calls(changed_diff):
    sig1 = sign_diff(changed_diff)
    sig2 = sign_diff(changed_diff)
    assert sig1.hexdigest == sig2.hexdigest


def test_sign_diff_values_do_not_affect_signature():
    """Two diffs with the same changed key but different values share a signature."""
    dr1 = DiffResult(left={"secret": "hunter2"}, right={"secret": "correct-horse"})
    dr2 = DiffResult(left={"secret": "aaaaa"}, right={"secret": "bbbbb"})
    assert sign_diff(dr1).hexdigest == sign_diff(dr2).hexdigest


def test_sign_diff_different_keys_differ():
    dr1 = DiffResult(left={"a": "1"}, right={"a": "2"})
    dr2 = DiffResult(left={"b": "1"}, right={"b": "2"})
    assert sign_diff(dr1).hexdigest != sign_diff(dr2).hexdigest


def test_sign_diff_short(changed_diff):
    sig = sign_diff(changed_diff)
    assert len(sig.short()) == 8
    assert sig.short(4) == sig.hexdigest[:4]


def test_sign_diff_as_dict_keys(changed_diff):
    d = sign_diff(changed_diff).as_dict()
    assert set(d.keys()) == {
        "hexdigest", "short", "key_count",
        "removed_count", "added_count", "changed_count",
    }


def test_sign_diff_md5_algorithm(changed_diff):
    sig = sign_diff(changed_diff, algorithm="md5")
    assert len(sig.hexdigest) == 32


# ---------------------------------------------------------------------------
# signatures_match
# ---------------------------------------------------------------------------

def test_signatures_match_same_diff(changed_diff):
    sig1 = sign_diff(changed_diff)
    sig2 = sign_diff(changed_diff)
    assert signatures_match(sig1, sig2)


def test_signatures_do_not_match_different_diffs(removed_diff, added_diff):
    sig1 = sign_diff(removed_diff)
    sig2 = sign_diff(added_diff)
    assert not signatures_match(sig1, sig2)
