"""Tests for stackdiff.filter."""

import pytest
from stackdiff.filter import filter_keys, apply_filters


@pytest.fixture()
def flat_cfg() -> dict[str, str]:
    return {
        "db.host": "localhost",
        "db.port": "5432",
        "app.debug": "true",
        "app.secret_key": "s3cr3t",
        "cache.ttl": "300",
    }


def test_filter_keys_no_filters(flat_cfg):
    assert filter_keys(flat_cfg) == flat_cfg


def test_filter_keys_include_exact(flat_cfg):
    result = filter_keys(flat_cfg, include=["db.host"])
    assert result == {"db.host": "localhost"}


def test_filter_keys_include_glob(flat_cfg):
    result = filter_keys(flat_cfg, include=["db.*"])
    assert set(result) == {"db.host", "db.port"}


def test_filter_keys_exclude_glob(flat_cfg):
    result = filter_keys(flat_cfg, exclude=["app.*"])
    assert "app.debug" not in result
    assert "app.secret_key" not in result
    assert "db.host" in result


def test_filter_keys_include_then_exclude(flat_cfg):
    result = filter_keys(flat_cfg, include=["app.*"], exclude=["*secret*"])
    assert set(result) == {"app.debug"}


def test_filter_keys_exclude_all(flat_cfg):
    result = filter_keys(flat_cfg, exclude=["*"])
    assert result == {}


def test_apply_filters_symmetry():
    a = {"db.host": "prod-db", "app.debug": "false"}
    b = {"db.host": "stage-db", "app.debug": "true"}
    fa, fb = apply_filters(a, b, include=["db.*"])
    assert set(fa) == {"db.host"}
    assert set(fb) == {"db.host"}


def test_apply_filters_exclude_sensitive():
    a = {"app.secret": "x", "app.name": "myapp"}
    b = {"app.secret": "y", "app.name": "myapp"}
    fa, fb = apply_filters(a, b, exclude=["*secret*"])
    assert "app.secret" not in fa
    assert "app.secret" not in fb
    assert "app.name" in fa
