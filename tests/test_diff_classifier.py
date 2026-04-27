"""Tests for stackdiff.diff_classifier."""

from __future__ import annotations

import pytest

from stackdiff.diff_engine import DiffResult
from stackdiff.diff_classifier import (
    ClassifiedDiff,
    ClassifiedKey,
    _infer_category,
    classify_diff,
)


@pytest.fixture
def sample_diff() -> DiffResult:
    staging = {
        "db_host": "localhost",
        "api_key": "old-key",
        "log_level": "debug",
        "app_name": "myapp",
    }
    production = {
        "db_host": "prod-db.internal",
        "api_key": "new-key",
        "service_port": "8080",
    }
    return DiffResult(
        staging=staging,
        production=production,
        added=["service_port"],
        removed=["log_level", "app_name"],
        changed=["db_host", "api_key"],
        label_a="staging",
        label_b="production",
    )


def test_infer_category_auth():
    assert _infer_category("api_key") == "auth"
    assert _infer_category("db_password") == "auth"


def test_infer_category_database():
    assert _infer_category("db_host") == "database"
    assert _infer_category("database_url") == "database"


def test_infer_category_network():
    assert _infer_category("service_port") == "network"
    assert _infer_category("endpoint_url") == "network"


def test_infer_category_logging():
    assert _infer_category("log_level") == "logging"


def test_infer_category_general_fallback():
    assert _infer_category("app_name") == "general"


def test_classify_diff_returns_classified_diff(sample_diff):
    result = classify_diff(sample_diff)
    assert isinstance(result, ClassifiedDiff)


def test_classify_diff_all_keys_present(sample_diff):
    result = classify_diff(sample_diff)
    all_keys = {ck.key for ck in result.all_keys()}
    assert all_keys == {"db_host", "api_key", "log_level", "app_name", "service_port"}


def test_classify_diff_db_host_in_database(sample_diff):
    result = classify_diff(sample_diff)
    db_keys = {ck.key for ck in result.keys_in_category("database")}
    assert "db_host" in db_keys


def test_classify_diff_api_key_in_auth(sample_diff):
    result = classify_diff(sample_diff)
    auth_keys = {ck.key for ck in result.keys_in_category("auth")}
    assert "api_key" in auth_keys


def test_classify_diff_change_types(sample_diff):
    result = classify_diff(sample_diff)
    by_key = {ck.key: ck for ck in result.all_keys()}
    assert by_key["service_port"].change_type == "added"
    assert by_key["log_level"].change_type == "removed"
    assert by_key["db_host"].change_type == "changed"


def test_classified_key_as_dict():
    ck = ClassifiedKey("db_host", "database", "changed", "localhost", "prod-db")
    d = ck.as_dict()
    assert d["key"] == "db_host"
    assert d["category"] == "database"
    assert d["change_type"] == "changed"


def test_classified_diff_as_dict(sample_diff):
    result = classify_diff(sample_diff)
    d = result.as_dict()
    assert isinstance(d, dict)
    for keys in d.values():
        assert isinstance(keys, list)
        assert all(isinstance(k, dict) for k in keys)


def test_empty_categories_excluded():
    empty_result = DiffResult(
        staging={}, production={},
        added=[], removed=[], changed=[],
        label_a="a", label_b="b",
    )
    result = classify_diff(empty_result)
    assert result.categories == {}
