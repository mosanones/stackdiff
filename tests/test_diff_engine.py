"""Tests for config_loader and diff_engine."""

import json
import textwrap
from pathlib import Path

import pytest

from stackdiff.config_loader import load_config, _flatten
from stackdiff.diff_engine import diff_configs, DiffResult


# --- _flatten ---

def test_flatten_simple():
    assert _flatten({"a": 1, "b": 2}) == {"a": 1, "b": 2}


def test_flatten_nested():
    data = {"db": {"host": "localhost", "port": 5432}}
    assert _flatten(data) == {"db.host": "localhost", "db.port": 5432}


def test_flatten_deeply_nested():
    data = {"a": {"b": {"c": "deep"}}}
    assert _flatten(data) == {"a.b.c": "deep"}


# --- load_config (dotenv + json via tmp files) ---

def test_load_dotenv(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text("HOST=localhost\n# comment\nPORT=5432\n")
    cfg = load_config(str(env_file))
    assert cfg == {"HOST": "localhost", "PORT": "5432"}


def test_load_json(tmp_path: Path):
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps({"app": {"debug": True, "workers": 4}}))
    cfg = load_config(str(cfg_file))
    assert cfg == {"app.debug": True, "app.workers": 4}


def test_load_missing_file():
    with pytest.raises(FileNotFoundError):
        load_config("/nonexistent/path.json")


def test_load_unsupported_format(tmp_path: Path):
    f = tmp_path / "config.toml"
    f.write_text("key = 'value'")
    with pytest.raises(ValueError, match="Unsupported"):
        load_config(str(f))


# --- diff_configs ---

def test_no_diff():
    cfg = {"A": "1", "B": "2"}
    result = diff_configs(cfg, cfg)
    assert not result.has_diff
    assert result.summary() == "No differences found."


def test_added_removed_changed():
    left = {"A": "1", "B": "old", "C": "3"}
    right = {"A": "1", "B": "new", "D": "4"}
    result = diff_configs(left, right)
    assert result.removed == {"C": "3"}
    assert result.added == {"D": "4"}
    assert result.changed == {"B": ("old", "new")}
    assert result.unchanged == {"A": "1"}
    assert result.has_diff


def test_ignore_keys():
    left = {"SECRET": "abc", "HOST": "staging.example.com"}
    right = {"SECRET": "xyz", "HOST": "prod.example.com"}
    result = diff_configs(left, right, ignore_keys=["SECRET"])
    assert "SECRET" not in result.changed
    assert "HOST" in result.changed
