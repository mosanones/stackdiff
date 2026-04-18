"""Tests for stackdiff.diff_cache."""

import time
import pytest
from stackdiff.diff_cache import save_cache, load_cache, clear_cache, list_cache_entries


@pytest.fixture
def cache_dir(tmp_path):
    return str(tmp_path / "cache")


@pytest.fixture
def cfg_pair():
    a = {"db.host": "localhost", "db.port": "5432"}
    b = {"db.host": "prod-db", "db.port": "5432"}
    return a, b


@pytest.fixture
def sample_result():
    return {"removed": {"db.host": "localhost"}, "added": {"db.host": "prod-db"}, "changed": {}}


def test_save_creates_file(cfg_pair, sample_result, cache_dir):
    a, b = cfg_pair
    path = save_cache(a, b, sample_result, cache_dir=cache_dir)
    assert path.exists()


def test_load_returns_result(cfg_pair, sample_result, cache_dir):
    a, b = cfg_pair
    save_cache(a, b, sample_result, cache_dir=cache_dir)
    loaded = load_cache(a, b, cache_dir=cache_dir)
    assert loaded == sample_result


def test_load_missing_returns_none(cfg_pair, cache_dir):
    a, b = cfg_pair
    result = load_cache(a, b, cache_dir=cache_dir)
    assert result is None


def test_load_expired_returns_none(cfg_pair, sample_result, cache_dir):
    a, b = cfg_pair
    save_cache(a, b, sample_result, cache_dir=cache_dir)
    time.sleep(0.05)
    result = load_cache(a, b, cache_dir=cache_dir, max_age=0.01)
    assert result is None


def test_load_within_max_age(cfg_pair, sample_result, cache_dir):
    a, b = cfg_pair
    save_cache(a, b, sample_result, cache_dir=cache_dir)
    result = load_cache(a, b, cache_dir=cache_dir, max_age=60)
    assert result is not None


def test_clear_cache_removes_files(cfg_pair, sample_result, cache_dir):
    a, b = cfg_pair
    save_cache(a, b, sample_result, cache_dir=cache_dir)
    removed = clear_cache(cache_dir=cache_dir)
    assert removed == 1
    assert load_cache(a, b, cache_dir=cache_dir) is None


def test_clear_cache_nonexistent_dir(cache_dir):
    removed = clear_cache(cache_dir=cache_dir + "_missing")
    assert removed == 0


def test_list_cache_entries(cfg_pair, sample_result, cache_dir):
    a, b = cfg_pair
    save_cache(a, b, sample_result, cache_dir=cache_dir)
    entries = list_cache_entries(cache_dir=cache_dir)
    assert len(entries) == 1
    assert "hash" in entries[0]
    assert "timestamp" in entries[0]


def test_different_configs_different_cache_keys(sample_result, cache_dir):
    a1, b1 = {"x": "1"}, {"x": "2"}
    a2, b2 = {"y": "1"}, {"y": "2"}
    save_cache(a1, b1, sample_result, cache_dir=cache_dir)
    save_cache(a2, b2, sample_result, cache_dir=cache_dir)
    assert len(list_cache_entries(cache_dir=cache_dir)) == 2
