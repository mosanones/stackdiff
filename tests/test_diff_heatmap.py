"""Tests for stackdiff.diff_heatmap."""
from __future__ import annotations

import pytest

from stackdiff.diff_engine import DiffResult
from stackdiff.diff_heatmap import DiffHeatmap, HeatmapEntry, build_heatmap


@pytest.fixture()
def dr_a() -> DiffResult:
    return DiffResult(
        label_a="staging",
        label_b="prod",
        removed={"db.host": "old"},
        added={"db.host": "new"},
        changed={"app.port": ("8080", "443")},
    )


@pytest.fixture()
def dr_b() -> DiffResult:
    return DiffResult(
        label_a="staging",
        label_b="prod",
        removed={},
        added={"app.debug": "true"},
        changed={"app.port": ("443", "80")},
    )


@pytest.fixture()
def dr_empty() -> DiffResult:
    return DiffResult(
        label_a="staging",
        label_b="prod",
        removed={},
        added={},
        changed={},
    )


def test_build_heatmap_returns_diff_heatmap(dr_a, dr_b):
    result = build_heatmap([dr_a, dr_b])
    assert isinstance(result, DiffHeatmap)


def test_total_diffs_recorded(dr_a, dr_b):
    result = build_heatmap([dr_a, dr_b])
    assert result.total_diffs == 2


def test_hottest_key_is_app_port(dr_a, dr_b):
    result = build_heatmap([dr_a, dr_b])
    assert result.hottest[0].key == "app.port"
    assert result.hottest[0].change_count == 2


def test_frequency_of_app_port(dr_a, dr_b):
    result = build_heatmap([dr_a, dr_b])
    entry = next(e for e in result.entries if e.key == "app.port")
    assert entry.frequency == pytest.approx(1.0)


def test_db_host_appears_once(dr_a, dr_b):
    result = build_heatmap([dr_a, dr_b])
    entry = next(e for e in result.entries if e.key == "db.host")
    assert entry.change_count == 1
    assert entry.frequency == pytest.approx(0.5)


def test_empty_diffs_list():
    result = build_heatmap([])
    assert result.total_diffs == 0
    assert result.entries == []


def test_all_empty_diffs(dr_empty):
    result = build_heatmap([dr_empty, dr_empty])
    assert result.entries == []


def test_as_dict_structure(dr_a, dr_b):
    result = build_heatmap([dr_a, dr_b])
    d = result.as_dict()
    assert "total_diffs" in d
    assert "entries" in d
    assert all("key" in e and "change_count" in e and "frequency" in e for e in d["entries"])


def test_heatmap_entry_as_dict():
    entry = HeatmapEntry(key="db.password", change_count=3, frequency=0.75)
    d = entry.as_dict()
    assert d == {"key": "db.password", "change_count": 3, "frequency": 0.75}
