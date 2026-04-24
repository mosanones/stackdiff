"""Tests for stackdiff.diff_normalizer."""

import pytest
from stackdiff.diff_normalizer import (
    NormalizeOptions,
    NormalizeResult,
    normalize_config,
    normalize_pair,
)


@pytest.fixture
def raw_cfg():
    return {
        "debug": "true",
        "port": "8080",
        "ratio": "0.75",
        "name": "  staging  ",
        "enabled": "yes",
        "verbose": "false",
    }


def test_normalize_config_returns_normalize_result(raw_cfg):
    result = normalize_config(raw_cfg)
    assert isinstance(result, NormalizeResult)


def test_coerce_boolean_true(raw_cfg):
    result = normalize_config(raw_cfg)
    assert result.config["debug"] is True
    assert result.config["enabled"] is True


def test_coerce_boolean_false(raw_cfg):
    result = normalize_config(raw_cfg)
    assert result.config["verbose"] is False


def test_coerce_integer(raw_cfg):
    result = normalize_config(raw_cfg)
    assert result.config["port"] == 8080
    assert isinstance(result.config["port"], int)


def test_coerce_float(raw_cfg):
    result = normalize_config(raw_cfg)
    assert result.config["ratio"] == pytest.approx(0.75)
    assert isinstance(result.config["ratio"], float)


def test_strip_whitespace(raw_cfg):
    result = normalize_config(raw_cfg)
    assert result.config["name"] == "staging"


def test_changes_logged(raw_cfg):
    result = normalize_config(raw_cfg)
    assert result.was_modified()
    assert any("debug" in c for c in result.changes)
    assert any("port" in c for c in result.changes)


def test_no_mutation_of_original(raw_cfg):
    original_copy = dict(raw_cfg)
    normalize_config(raw_cfg)
    assert raw_cfg == original_copy


def test_lowercase_keys_option():
    cfg = {"HOST": "localhost", "PORT": "5432"}
    opts = NormalizeOptions(lowercase_keys=True)
    result = normalize_config(cfg, opts)
    assert "host" in result.config
    assert "port" in result.config
    assert "HOST" not in result.config


def test_alias_renames_key():
    cfg = {"db_host": "localhost"}
    opts = NormalizeOptions(aliases={"db_host": "database.host"})
    result = normalize_config(cfg, opts)
    assert "database.host" in result.config
    assert "db_host" not in result.config
    assert any("alias" in c for c in result.changes)


def test_disable_coerce_booleans():
    cfg = {"flag": "true"}
    opts = NormalizeOptions(coerce_booleans=False)
    result = normalize_config(cfg, opts)
    assert result.config["flag"] == "true"


def test_disable_coerce_numbers():
    cfg = {"port": "8080"}
    opts = NormalizeOptions(coerce_numbers=False, coerce_booleans=False)
    result = normalize_config(cfg, opts)
    assert result.config["port"] == "8080"


def test_normalize_pair_returns_two_dicts():
    left = {"port": "3000"}
    right = {"port": "4000"}
    l, r = normalize_pair(left, right)
    assert l["port"] == 3000
    assert r["port"] == 4000


def test_non_string_values_pass_through():
    cfg = {"count": 42, "active": True, "ratio": 1.5}
    result = normalize_config(cfg)
    assert result.config == cfg
    assert not result.was_modified()
