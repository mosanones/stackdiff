"""Tests for stackdiff.scorer."""
import pytest
from stackdiff.diff_engine import DiffResult
from stackdiff.annotator import annotate, Severity
from stackdiff.scorer import score_annotated, score_diff, DiffScore, _label


@pytest.fixture
def simple_diff():
    return DiffResult(
        removed={"db.password": "old"},
        added={"db.password": "new"},
        changed={"db.password": ("old", "new")},
        unchanged={},
    )


@pytest.fixture
def multi_diff():
    return DiffResult(
        removed={"host": "a"},
        added={"host": "b", "token": "x"},
        changed={"host": ("a", "b"), "token": (None, "x")},
        unchanged={"port": "5432"},
    )


def test_label_clean():
    assert _label(0) == "clean"


def test_label_low_risk():
    assert _label(5) == "low-risk"


def test_label_moderate():
    assert _label(15) == "moderate"


def test_label_high_risk():
    assert _label(50) == "high-risk"


def test_score_diff_no_changes():
    empty = DiffResult(removed={}, added={}, changed={}, unchanged={"a": "1"})
    s = score_diff(empty)
    assert s.total == 0
    assert s.label == "clean"


def test_score_diff_counts_changes(multi_diff):
    s = score_diff(multi_diff)
    assert s.low == 3  # host + token + removed host
    assert s.total == 3


def test_score_diff_returns_diff_score(simple_diff):
    s = score_diff(simple_diff)
    assert isinstance(s, DiffScore)


def test_score_annotated_critical_weighted(simple_diff):
    ann = annotate(simple_diff)
    s = score_annotated(ann)
    assert s.critical >= 1
    assert s.total >= 10


def test_score_annotated_label_high_risk(simple_diff):
    ann = annotate(simple_diff)
    s = score_annotated(ann)
    assert s.label in ("moderate", "high-risk")


def test_score_annotated_as_dict(simple_diff):
    ann = annotate(simple_diff)
    d = score_annotated(ann).as_dict()
    assert set(d.keys()) == {"total", "critical", "high", "medium", "low", "label"}


def test_score_annotated_empty_diff():
    empty = DiffResult(removed={}, added={}, changed={}, unchanged={})
    ann = annotate(empty)
    s = score_annotated(ann)
    assert s.total == 0
    assert s.label == "clean"
