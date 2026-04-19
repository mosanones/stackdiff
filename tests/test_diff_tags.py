import pytest
from stackdiff.diff_tags import (
    tag_diff_keys,
    filter_by_tag,
    _infer_tags,
    TaggedDiff,
    TaggedKey,
)


@pytest.fixture
def keys():
    return ["db_host", "db_password", "api_key", "log_level", "feature_dark_mode", "app_name"]


def test_tag_diff_keys_returns_tagged_diff(keys):
    result = tag_diff_keys(keys)
    assert isinstance(result, TaggedDiff)


def test_all_keys_present(keys):
    result = tag_diff_keys(keys)
    result_keys = [tk.key for tk in result.tagged_keys]
    for k in keys:
        assert k in result_keys


def test_db_host_tagged_database_and_network(keys):
    result = tag_diff_keys(keys)
    tk = next(t for t in result.tagged_keys if t.key == "db_host")
    assert "database" in tk.tags
    assert "network" in tk.tags


def test_api_key_tagged_auth(keys):
    result = tag_diff_keys(keys)
    tk = next(t for t in result.tagged_keys if t.key == "api_key")
    assert "auth" in tk.tags


def test_app_name_has_no_tags(keys):
    result = tag_diff_keys(keys)
    tk = next(t for t in result.tagged_keys if t.key == "app_name")
    assert tk.tags == []


def test_tag_index_built_correctly(keys):
    result = tag_diff_keys(keys)
    assert "db_host" in result.tag_index.get("database", [])
    assert "log_level" in result.tag_index.get("logging", [])


def test_filter_by_tag(keys):
    result = tag_diff_keys(keys)
    db_keys = filter_by_tag(result, "database")
    assert "db_host" in db_keys
    assert "db_password" in db_keys


def test_filter_by_missing_tag(keys):
    result = tag_diff_keys(keys)
    assert filter_by_tag(result, "nonexistent") == []


def test_extra_rules_applied():
    keys = ["cache_ttl", "cache_host"]
    result = tag_diff_keys(keys, extra_rules={"cache": ["cache_"]})
    assert "cache_ttl" in result.tag_index.get("cache", [])


def test_as_dict_structure(keys):
    result = tag_diff_keys(keys)
    d = result.as_dict()
    assert "tagged_keys" in d
    assert "tag_index" in d
    assert isinstance(d["tagged_keys"], list)
