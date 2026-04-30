"""Tests for stackdiff.diff_cluster."""
import pytest

from stackdiff.diff_engine import DiffResult
from stackdiff.diff_cluster import (
    ClusterEntry,
    DiffCluster,
    _infer_cluster,
    cluster_diff,
)


@pytest.fixture()
def sample_diff() -> DiffResult:
    return DiffResult(
        removed={"db_host": "old-db", "api_key": "abc123"},
        added={"log_level": "debug", "feature_new_ui": "true"},
        changed={
            "db_port": ("5432", "5433"),
            "auth_token": ("tok-old", "tok-new"),
            "app_name": ("myapp", "myapp-v2"),
        },
    )


@pytest.fixture()
def empty_diff() -> DiffResult:
    return DiffResult(removed={}, added={}, changed={})


def test_cluster_diff_returns_diff_cluster(sample_diff):
    result = cluster_diff(sample_diff)
    assert isinstance(result, DiffCluster)


def test_cluster_diff_empty_has_no_active_clusters(empty_diff):
    result = cluster_diff(empty_diff)
    assert result.cluster_names == []


def test_db_host_in_database_cluster(sample_diff):
    result = cluster_diff(sample_diff)
    keys = [e.key for e in result.keys_in_cluster("database")]
    assert "db_host" in keys


def test_db_port_in_database_cluster(sample_diff):
    result = cluster_diff(sample_diff)
    keys = [e.key for e in result.keys_in_cluster("database")]
    assert "db_port" in keys


def test_api_key_in_auth_cluster(sample_diff):
    result = cluster_diff(sample_diff)
    keys = [e.key for e in result.keys_in_cluster("auth")]
    assert "api_key" in keys


def test_auth_token_in_auth_cluster(sample_diff):
    result = cluster_diff(sample_diff)
    keys = [e.key for e in result.keys_in_cluster("auth")]
    assert "auth_token" in keys


def test_log_level_in_logging_cluster(sample_diff):
    result = cluster_diff(sample_diff)
    keys = [e.key for e in result.keys_in_cluster("logging")]
    assert "log_level" in keys


def test_feature_flag_in_feature_flags_cluster(sample_diff):
    result = cluster_diff(sample_diff)
    keys = [e.key for e in result.keys_in_cluster("feature_flags")]
    assert "feature_new_ui" in keys


def test_misc_key_goes_to_misc(sample_diff):
    result = cluster_diff(sample_diff)
    keys = [e.key for e in result.keys_in_cluster("misc")]
    assert "app_name" in keys


def test_cluster_entry_change_type_removed(sample_diff):
    result = cluster_diff(sample_diff)
    db_entries = {e.key: e for e in result.keys_in_cluster("database")}
    assert db_entries["db_host"].change_type == "removed"


def test_cluster_entry_change_type_added(sample_diff):
    result = cluster_diff(sample_diff)
    log_entries = {e.key: e for e in result.keys_in_cluster("logging")}
    assert log_entries["log_level"].change_type == "added"


def test_cluster_entry_change_type_changed(sample_diff):
    result = cluster_diff(sample_diff)
    db_entries = {e.key: e for e in result.keys_in_cluster("database")}
    assert db_entries["db_port"].change_type == "changed"


def test_as_dict_structure(sample_diff):
    result = cluster_diff(sample_diff)
    d = result.as_dict()
    assert isinstance(d, dict)
    assert "database" in d
    assert isinstance(d["database"], list)
    assert "key" in d["database"][0]


def test_infer_cluster_auth():
    assert _infer_cluster("auth_password") == "auth"


def test_infer_cluster_network():
    assert _infer_cluster("service_host") == "network"


def test_infer_cluster_misc():
    assert _infer_cluster("app_version") == "misc"


def test_cluster_names_only_non_empty(sample_diff):
    result = cluster_diff(sample_diff)
    for name in result.cluster_names:
        assert len(result.keys_in_cluster(name)) > 0
