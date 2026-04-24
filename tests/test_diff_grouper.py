"""Tests for stackdiff.diff_grouper."""
from __future__ import annotations

import pytest

from stackdiff.diff_engine import DiffResult
from stackdiff.diff_grouper import (
    GroupedDiff,
    KeyGroup,
    group_by_custom,
    group_by_namespace,
)


@pytest.fixture()
def flat_diff() -> DiffResult:
    return DiffResult(
        removed={"db.host": "old"},
        added={"db.port": "5433"},
        changed={"app.debug": ("true", "false"), "timeout": ("30", "60")},
    )


@pytest.fixture()
def empty_diff() -> DiffResult:
    return DiffResult(removed={}, added={}, changed={})


def test_group_by_namespace_returns_grouped_diff(flat_diff):
    result = group_by_namespace(flat_diff)
    assert isinstance(result, GroupedDiff)


def test_group_by_namespace_groups_db_keys(flat_diff):
    result = group_by_namespace(flat_diff)
    assert "db" in result.groups
    assert set(result.groups["db"].keys) == {"db.host", "db.port"}


def test_group_by_namespace_groups_app_keys(flat_diff):
    result = group_by_namespace(flat_diff)
    assert "app" in result.groups
    assert "app.debug" in result.groups["app"].keys


def test_group_by_namespace_ungrouped_flat_key(flat_diff):
    result = group_by_namespace(flat_diff)
    assert "timeout" in result.ungrouped


def test_group_by_namespace_empty_diff(empty_diff):
    result = group_by_namespace(empty_diff)
    assert result.groups == {}
    assert result.ungrouped == []


def test_group_by_custom_assigns_keys(flat_diff):
    mapping = {"database": ["db"], "application": ["app"]}
    result = group_by_custom(flat_diff, mapping)
    assert "database" in result.groups
    assert "db.host" in result.groups["database"].keys
    assert "db.port" in result.groups["database"].keys


def test_group_by_custom_ungrouped_remainder(flat_diff):
    mapping = {"database": ["db"]}
    result = group_by_custom(flat_diff, mapping)
    assert "timeout" in result.ungrouped
    assert "app.debug" in result.ungrouped


def test_group_by_custom_empty_mapping_all_ungrouped(flat_diff):
    result = group_by_custom(flat_diff, {})
    all_keys = set(result.ungrouped)
    assert "timeout" in all_keys
    assert "db.host" in all_keys


def test_key_group_as_dict():
    grp = KeyGroup(name="db", keys=["db.host"])
    d = grp.as_dict()
    assert d["name"] == "db"
    assert d["keys"] == ["db.host"]


def test_grouped_diff_as_dict(flat_diff):
    result = group_by_namespace(flat_diff)
    d = result.as_dict()
    assert "groups" in d
    assert "ungrouped" in d
