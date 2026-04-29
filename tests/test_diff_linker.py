"""Tests for diff_linker, linker_formatter, and linker_cli."""
from __future__ import annotations

import json
import textwrap

import pytest

from stackdiff.diff_linker import LinkedKey, LinkedDiff, link_diffs, link_from_diff_results
from stackdiff.diff_engine import DiffResult
from stackdiff.linker_formatter import (
    format_linked_text,
    format_linked_json,
    format_linked_output,
)
from stackdiff.linker_cli import build_linker_parser, main


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def three_envs() -> dict:
    return {
        "dev":     {"db.host": "localhost", "app.debug": "true",  "api.key": "devkey"},
        "staging": {"db.host": "staging-db", "app.debug": "false", "api.key": "stagkey"},
        "prod":    {"db.host": "prod-db",    "app.debug": "false"},  # api.key absent
    }


@pytest.fixture()
def linked(three_envs) -> LinkedDiff:
    return link_diffs(three_envs)


# ---------------------------------------------------------------------------
# link_diffs
# ---------------------------------------------------------------------------

def test_link_diffs_returns_linked_diff(linked):
    assert isinstance(linked, LinkedDiff)


def test_link_diffs_env_names(linked):
    assert linked.env_names == ["dev", "staging", "prod"]


def test_link_diffs_all_keys_present(linked):
    keys = {lk.key for lk in linked.keys}
    assert keys == {"db.host", "app.debug", "api.key"}


def test_linked_key_missing_in(linked):
    api_key = next(lk for lk in linked.keys if lk.key == "api.key")
    assert api_key.missing_in == ["prod"]


def test_linked_key_is_consistent_same_value(linked):
    debug = next(lk for lk in linked.keys if lk.key == "app.debug")
    # dev=true, staging=false → inconsistent
    assert not debug.is_consistent


def test_linked_key_inconsistent_keys(linked):
    inc = {lk.key for lk in linked.inconsistent_keys()}
    assert "db.host" in inc
    assert "api.key" in inc  # absent in prod


def test_link_from_diff_results():
    dr = DiffResult(
        removed={"old.key": "v1"},
        added={"new.key": "v2"},
        changed={"shared.key": ("a", "b")},
    )
    result = link_from_diff_results({"env_a": dr, "env_b": dr})
    assert isinstance(result, LinkedDiff)
    assert len(result.env_names) == 2


# ---------------------------------------------------------------------------
# linker_formatter
# ---------------------------------------------------------------------------

def test_format_linked_text_contains_header(linked):
    out = format_linked_text(linked)
    assert "KEY" in out
    assert "dev" in out
    assert "prod" in out


def test_format_linked_text_marks_inconsistent(linked):
    out = format_linked_text(linked)
    assert "!" in out


def test_format_linked_text_shows_absent(linked):
    out = format_linked_text(linked)
    assert "<absent>" in out


def test_format_linked_json_valid(linked):
    raw = format_linked_json(linked)
    data = json.loads(raw)
    assert "environments" in data
    assert "keys" in data
    assert data["summary"]["total_keys"] == 3


def test_format_linked_output_dispatches(linked):
    assert format_linked_output(linked, fmt="text") == format_linked_text(linked)
    assert format_linked_output(linked, fmt="json") == format_linked_json(linked)


# ---------------------------------------------------------------------------
# linker_cli
# ---------------------------------------------------------------------------

def test_build_linker_parser_returns_parser():
    p = build_linker_parser()
    assert p is not None


def test_main_text_output(tmp_path):
    a = tmp_path / "a.yaml"
    b = tmp_path / "b.yaml"
    a.write_text("db_host: localhost\napi_key: secret\n")
    b.write_text("db_host: prod-db\napi_key: secret\n")
    rc = main([f"staging:{a}", f"prod:{b}", "--format", "text"])
    assert rc == 0


def test_main_json_output(tmp_path):
    a = tmp_path / "a.yaml"
    b = tmp_path / "b.yaml"
    a.write_text("x: 1\n")
    b.write_text("x: 2\n")
    rc = main([f"env1:{a}", f"env2:{b}", "--format", "json"])
    assert rc == 0


def test_main_bad_env_arg_returns_2():
    rc = main(["no-colon-here"])
    assert rc == 2


def test_main_missing_file_returns_2():
    rc = main(["env1:/nonexistent/path.yaml"])
    assert rc == 2
