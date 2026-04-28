"""Tests for diff_blame, blame_formatter, and blame_cli."""
from __future__ import annotations

import json
import pytest

from stackdiff.diff_engine import DiffResult
from stackdiff.diff_blame import blame_diff, BlamedDiff, BlameEntry, _infer_source
from stackdiff.blame_formatter import (
    format_blamed_text,
    format_blamed_json,
    format_blamed_output,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def sample_result() -> DiffResult:
    return DiffResult(
        removed={"db.password": "old_pass", "app.debug": "true"},
        added={"api.endpoint": "https://prod.example.com"},
        changed={"db.host": ("staging-db", "prod-db"), "env": ("staging", "production")},
    )


@pytest.fixture()
def blamed(sample_result: DiffResult) -> BlamedDiff:
    return blame_diff(sample_result)


# ---------------------------------------------------------------------------
# _infer_source
# ---------------------------------------------------------------------------

def test_infer_source_secret():
    assert _infer_source("db.password") == "secret"


def test_infer_source_infra():
    assert _infer_source("db.host") == "infra"


def test_infer_source_app():
    assert _infer_source("app.debug") == "app"


def test_infer_source_env():
    assert _infer_source("env") == "env"


def test_infer_source_unknown():
    assert _infer_source("completely_random_key_xyz") == "unknown"


# ---------------------------------------------------------------------------
# blame_diff
# ---------------------------------------------------------------------------

def test_blame_diff_returns_blamed_diff(blamed):
    assert isinstance(blamed, BlamedDiff)


def test_blame_diff_all_keys_present(blamed, sample_result):
    all_keys = {e.key for e in blamed.entries}
    expected = (
        set(sample_result.removed)
        | set(sample_result.added)
        | set(sample_result.changed)
    )
    assert all_keys == expected


def test_blame_diff_change_types(blamed):
    types = {e.change_type for e in blamed.entries}
    assert types == {"removed", "added", "changed"}


def test_blame_diff_entries_sorted_by_source_then_key(blamed):
    pairs = [(e.source, e.key) for e in blamed.entries]
    assert pairs == sorted(pairs)


def test_by_source_filters_correctly(blamed):
    secret_entries = blamed.by_source("secret")
    assert all(e.source == "secret" for e in secret_entries)
    assert any(e.key == "db.password" for e in secret_entries)


def test_sources_present_no_duplicates(blamed):
    sources = blamed.sources_present()
    assert len(sources) == len(set(sources))


def test_as_dict_structure(blamed):
    d = blamed.as_dict()
    assert "entries" in d
    assert isinstance(d["entries"], list)
    first = d["entries"][0]
    assert {"key", "change_type", "old_value", "new_value", "source"} <= first.keys()


# ---------------------------------------------------------------------------
# Formatter
# ---------------------------------------------------------------------------

def test_format_blamed_text_contains_header(blamed):
    out = format_blamed_text(blamed)
    assert "Blame report" in out


def test_format_blamed_text_shows_source_section(blamed):
    out = format_blamed_text(blamed)
    assert "[SECRET]" in out or "[INFRA]" in out or "[APP]" in out


def test_format_blamed_text_no_diff():
    empty = BlamedDiff(entries=[])
    assert "No differences" in format_blamed_text(empty)


def test_format_blamed_json_valid(blamed):
    out = format_blamed_json(blamed)
    parsed = json.loads(out)
    assert "entries" in parsed


def test_format_blamed_output_json(blamed):
    out = format_blamed_output(blamed, fmt="json")
    parsed = json.loads(out)
    assert "entries" in parsed


def test_format_blamed_output_text(blamed):
    out = format_blamed_output(blamed, fmt="text")
    assert "Blame report" in out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def test_blame_cli_exit_zero(tmp_path):
    import yaml
    from stackdiff.blame_cli import main

    a = tmp_path / "a.yaml"
    b = tmp_path / "b.yaml"
    a.write_text(yaml.dump({"db.host": "staging", "api.key": "s3cr3t"}))
    b.write_text(yaml.dump({"db.host": "prod", "api.key": "s3cr3t"}))

    rc = main([str(a), str(b)])
    assert rc == 0


def test_blame_cli_fail_on_diff(tmp_path):
    import yaml
    from stackdiff.blame_cli import main

    a = tmp_path / "a.yaml"
    b = tmp_path / "b.yaml"
    a.write_text(yaml.dump({"db.host": "staging"}))
    b.write_text(yaml.dump({"db.host": "prod"}))

    rc = main([str(a), str(b), "--fail-on-diff"])
    assert rc == 1


def test_blame_cli_json_output(tmp_path, capsys):
    import yaml
    from stackdiff.blame_cli import main

    a = tmp_path / "a.yaml"
    b = tmp_path / "b.yaml"
    a.write_text(yaml.dump({"db.host": "staging"}))
    b.write_text(yaml.dump({"db.host": "prod"}))

    main([str(a), str(b), "--format", "json"])
    captured = capsys.readouterr()
    parsed = json.loads(captured.out)
    assert "entries" in parsed
