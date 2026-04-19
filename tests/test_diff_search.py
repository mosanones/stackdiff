import pytest
from stackdiff.diff_engine import DiffResult
from stackdiff.diff_search import SearchQuery, SearchResult, search_diff


@pytest.fixture
def sample_diff():
    return DiffResult(
        added={"db.host": "prod-db", "feature.flag": "true"},
        removed={"old.key": "legacy"},
        changed={"api.url": ("http://staging", "http://prod"), "db.port": ("5432", "5433")},
    )


def test_search_no_filters_returns_all(sample_diff):
    result = search_diff(sample_diff, SearchQuery())
    assert result.count() == 5


def test_search_by_key_pattern(sample_diff):
    result = search_diff(sample_diff, SearchQuery(key_pattern="db.*"))
    assert "db.host" in result.matches
    assert "db.port" in result.matches
    assert "api.url" not in result.matches


def test_search_by_change_type_added(sample_diff):
    result = search_diff(sample_diff, SearchQuery(change_type="added"))
    assert set(result.matches.keys()) == {"db.host", "feature.flag"}


def test_search_by_change_type_removed(sample_diff):
    result = search_diff(sample_diff, SearchQuery(change_type="removed"))
    assert set(result.matches.keys()) == {"old.key"}


def test_search_by_change_type_changed(sample_diff):
    result = search_diff(sample_diff, SearchQuery(change_type="changed"))
    assert "api.url" in result.matches
    assert "db.port" in result.matches


def test_search_by_value_contains(sample_diff):
    result = search_diff(sample_diff, SearchQuery(value_contains="prod"))
    assert "db.host" in result.matches
    assert "api.url" in result.matches


def test_search_combined_filters(sample_diff):
    result = search_diff(sample_diff, SearchQuery(key_pattern="db.*", change_type="changed"))
    assert result.count() == 1
    assert "db.port" in result.matches


def test_search_no_matches(sample_diff):
    result = search_diff(sample_diff, SearchQuery(key_pattern="nonexistent.*"))
    assert result.count() == 0


def test_search_result_as_dict(sample_diff):
    result = search_diff(sample_diff, SearchQuery(change_type="added"))
    d = result.as_dict()
    assert "matches" in d
    assert d["count"] == 2


def test_match_entry_has_change_type_and_value(sample_diff):
    result = search_diff(sample_diff, SearchQuery(key_pattern="old.key"))
    entry = result.matches["old.key"]
    assert entry["change_type"] == "removed"
    assert "legacy" in entry["value"]
