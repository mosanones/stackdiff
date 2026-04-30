"""Tests for diff_matrix.py and matrix_formatter.py."""
import json
import pytest

from stackdiff.diff_matrix import (
    MatrixCell,
    DiffMatrix,
    build_matrix,
    _count_changes,
)
from stackdiff.matrix_formatter import (
    format_matrix_text,
    format_matrix_json,
    format_matrix_output,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def three_envs():
    return {
        "dev":     {"db.host": "localhost", "app.port": "8000", "log.level": "debug"},
        "staging": {"db.host": "staging-db", "app.port": "8000", "log.level": "info"},
        "prod":    {"db.host": "prod-db",    "app.port": "443",  "log.level": "warn"},
    }


@pytest.fixture
def identical_envs():
    cfg = {"key": "value", "other": "123"}
    return {"a": cfg.copy(), "b": cfg.copy()}


# ---------------------------------------------------------------------------
# MatrixCell
# ---------------------------------------------------------------------------

def test_matrix_cell_total():
    cell = MatrixCell(left="a", right="b", added=1, removed=2, changed=3)
    assert cell.total == 6


def test_matrix_cell_has_diff_true():
    cell = MatrixCell(left="a", right="b", added=0, removed=1, changed=0)
    assert cell.has_diff is True


def test_matrix_cell_has_diff_false():
    cell = MatrixCell(left="a", right="b", added=0, removed=0, changed=0)
    assert cell.has_diff is False


def test_matrix_cell_as_dict_keys():
    cell = MatrixCell(left="x", right="y", added=1, removed=0, changed=2)
    d = cell.as_dict()
    assert set(d.keys()) == {"left", "right", "added", "removed", "changed", "total", "has_diff"}


# ---------------------------------------------------------------------------
# build_matrix
# ---------------------------------------------------------------------------

def test_build_matrix_returns_diff_matrix(three_envs):
    result = build_matrix(three_envs)
    assert isinstance(result, DiffMatrix)


def test_build_matrix_correct_pair_count(three_envs):
    # 3 envs => C(3,2) = 3 pairs
    result = build_matrix(three_envs)
    assert len(result.cells) == 3


def test_build_matrix_env_names(three_envs):
    result = build_matrix(three_envs)
    assert result.env_names == ["dev", "staging", "prod"]


def test_build_matrix_detects_diffs(three_envs):
    result = build_matrix(three_envs)
    assert any(c.has_diff for c in result.cells)


def test_build_matrix_identical_envs(identical_envs):
    result = build_matrix(identical_envs)
    assert len(result.cells) == 1
    assert result.cells[0].has_diff is False


def test_build_matrix_get_cell(three_envs):
    result = build_matrix(three_envs)
    cell = result.get_cell("dev", "staging")
    assert cell is not None
    assert cell.left == "dev"
    assert cell.right == "staging"


def test_build_matrix_get_cell_missing(three_envs):
    result = build_matrix(three_envs)
    assert result.get_cell("staging", "dev") is None


def test_pairs_with_diff(three_envs):
    result = build_matrix(three_envs)
    pairs = result.pairs_with_diff()
    assert all(c.has_diff for c in pairs)


# ---------------------------------------------------------------------------
# matrix_formatter
# ---------------------------------------------------------------------------

def test_format_matrix_text_contains_header(three_envs):
    matrix = build_matrix(three_envs)
    out = format_matrix_text(matrix)
    assert "Diff Matrix" in out


def test_format_matrix_text_shows_pair(three_envs):
    matrix = build_matrix(three_envs)
    out = format_matrix_text(matrix)
    assert "dev <-> staging" in out


def test_format_matrix_text_empty():
    matrix = DiffMatrix(env_names=[])
    out = format_matrix_text(matrix)
    assert "No environment pairs" in out


def test_format_matrix_json_valid(three_envs):
    matrix = build_matrix(three_envs)
    out = format_matrix_json(matrix)
    data = json.loads(out)
    assert "cells" in data
    assert "env_names" in data


def test_format_matrix_output_text(three_envs):
    matrix = build_matrix(three_envs)
    assert "Diff Matrix" in format_matrix_output(matrix, fmt="text")


def test_format_matrix_output_json(three_envs):
    matrix = build_matrix(three_envs)
    out = format_matrix_output(matrix, fmt="json")
    assert json.loads(out)
