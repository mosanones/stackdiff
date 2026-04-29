"""Tests for stackdiff.diff_embedder."""
from __future__ import annotations

import math
import pytest

from stackdiff.diff_engine import DiffResult
from stackdiff.diff_embedder import DiffVector, embed_diff


# ------------------------------------------------------------------ #
# fixtures
# ------------------------------------------------------------------ #

@pytest.fixture()
def empty_diff() -> DiffResult:
    return DiffResult(label_a="staging", label_b="prod", added={}, removed={}, changed={})


@pytest.fixture()
def simple_diff() -> DiffResult:
    return DiffResult(
        label_a="staging",
        label_b="prod",
        added={"db.port": "5433"},
        removed={"db.host": "old-host"},
        changed={"app.password": ("secret1", "secret2"), "api.endpoint": ("http://a", "http://b")},
    )


@pytest.fixture()
def large_diff() -> DiffResult:
    added = {f"key.added.{i}": str(i) for i in range(20)}
    removed = {f"key.removed.{i}": str(i) for i in range(10)}
    changed = {f"key.changed.{i}": (str(i), str(i + 1)) for i in range(30)}
    return DiffResult(label_a="a", label_b="b", added=added, removed=removed, changed=changed)


# ------------------------------------------------------------------ #
# DiffVector tests
# ------------------------------------------------------------------ #

def test_embed_diff_returns_diff_vector(simple_diff):
    vec = embed_diff(simple_diff)
    assert isinstance(vec, DiffVector)


def test_dimensions_length(simple_diff):
    vec = embed_diff(simple_diff)
    assert len(vec.dimensions) == len(vec.DIMENSION_NAMES)


def test_dimension_names_count():
    vec = DiffVector(label_a="a", label_b="b", dimensions=[])
    assert len(vec.DIMENSION_NAMES) == 8


def test_labels_preserved(simple_diff):
    vec = embed_diff(simple_diff)
    assert vec.label_a == "staging"
    assert vec.label_b == "prod"


def test_total_changes_dimension(simple_diff):
    vec = embed_diff(simple_diff)
    # added=1, removed=1, changed=2  → total=4
    assert vec.dimensions[0] == pytest.approx(4.0)


def test_ratios_sum_to_one(simple_diff):
    vec = embed_diff(simple_diff)
    total = vec.dimensions[0]
    added_r, removed_r, changed_r = vec.dimensions[1], vec.dimensions[2], vec.dimensions[3]
    assert added_r + removed_r + changed_r == pytest.approx(1.0)


def test_score_normalised_in_range(simple_diff):
    vec = embed_diff(simple_diff)
    assert 0.0 <= vec.dimensions[6] <= 1.0


def test_log_total_positive(simple_diff):
    vec = embed_diff(simple_diff)
    assert vec.dimensions[7] > 0.0


def test_empty_diff_total_zero(empty_diff):
    vec = embed_diff(empty_diff)
    assert vec.dimensions[0] == 0.0


def test_empty_diff_log_total_zero(empty_diff):
    vec = embed_diff(empty_diff)
    # log1p(0) == 0
    assert vec.dimensions[7] == pytest.approx(0.0)


def test_as_dict_has_expected_keys(simple_diff):
    d = embed_diff(simple_diff).as_dict()
    assert set(d.keys()) == {"label_a", "label_b", "dimensions"}
    assert isinstance(d["dimensions"], dict)


def test_magnitude_positive(simple_diff):
    vec = embed_diff(simple_diff)
    assert vec.magnitude() > 0.0


def test_cosine_similarity_self(simple_diff):
    vec = embed_diff(simple_diff)
    assert vec.cosine_similarity(vec) == pytest.approx(1.0)


def test_cosine_similarity_zero_vector(empty_diff, simple_diff):
    # empty diff produces a zero-ish vector; cosine should not raise
    vec_empty = embed_diff(empty_diff)
    vec_simple = embed_diff(simple_diff)
    result = vec_empty.cosine_similarity(vec_simple)
    assert isinstance(result, float)


def test_large_diff_log_total(large_diff):
    vec = embed_diff(large_diff)
    expected = math.log1p(60)
    assert vec.dimensions[7] == pytest.approx(expected)
