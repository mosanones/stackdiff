"""Tests for stackdiff/diff_explainer.py"""

import pytest
from stackdiff.diff_engine import DiffResult
from stackdiff.annotator import AnnotatedDiff, Annotation, annotate_diff
from stackdiff.diff_explainer import (
    DiffExplanation,
    Explanation,
    explain_annotated,
)


@pytest.fixture
def sample_diff():
    return DiffResult(
        removed={"db.password": "old_secret"},
        added={"feature.new_flag": "true"},
        changed={"api.endpoint": ("http://old", "http://new")},
    )


@pytest.fixture
def annotated(sample_diff):
    return annotate_diff(sample_diff)


def test_explain_annotated_returns_diff_explanation(annotated):
    result = explain_annotated(annotated)
    assert isinstance(result, DiffExplanation)


def test_all_keys_have_explanations(annotated, sample_diff):
    result = explain_annotated(annotated)
    keys = {e.key for e in result.explanations}
    assert "db.password" in keys
    assert "feature.new_flag" in keys
    assert "api.endpoint" in keys


def test_removed_key_change_type(annotated):
    result = explain_annotated(annotated)
    removed = next(e for e in result.explanations if e.key == "db.password")
    assert removed.change_type == "removed"
    assert removed.new_value is None
    assert removed.old_value == "old_secret"


def test_added_key_change_type(annotated):
    result = explain_annotated(annotated)
    added = next(e for e in result.explanations if e.key == "feature.new_flag")
    assert added.change_type == "added"
    assert added.old_value is None
    assert added.new_value == "true"


def test_changed_key_change_type(annotated):
    result = explain_annotated(annotated)
    changed = next(e for e in result.explanations if e.key == "api.endpoint")
    assert changed.change_type == "changed"
    assert changed.old_value == "http://old"
    assert changed.new_value == "http://new"


def test_critical_severity_for_password(annotated):
    result = explain_annotated(annotated)
    password_exp = next(e for e in result.explanations if e.key == "db.password")
    assert password_exp.severity == "critical"


def test_message_is_non_empty(annotated):
    result = explain_annotated(annotated)
    for exp in result.explanations:
        assert isinstance(exp.message, str)
        assert len(exp.message) > 0


def test_removed_message_mentions_key(annotated):
    result = explain_annotated(annotated)
    removed = next(e for e in result.explanations if e.key == "db.password")
    assert "db.password" in removed.message


def test_critical_sorted_first(annotated):
    result = explain_annotated(annotated)
    if len(result.explanations) > 1:
        severities = [e.severity for e in result.explanations]
        order = ["critical", "high", "medium", "low"]
        ranked = [order.index(s) if s in order else 99 for s in severities]
        assert ranked == sorted(ranked)


def test_as_dict_structure(annotated):
    result = explain_annotated(annotated)
    d = result.as_dict()
    assert "explanations" in d
    assert isinstance(d["explanations"], list)
    for item in d["explanations"]:
        assert "key" in item
        assert "change_type" in item
        assert "message" in item
        assert "severity" in item
        assert "category" in item


def test_empty_diff_produces_no_explanations():
    empty = DiffResult(removed={}, added={}, changed={})
    from stackdiff.annotator import annotate_diff
    ann = annotate_diff(empty)
    result = explain_annotated(ann)
    assert result.explanations == []
