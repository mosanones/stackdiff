"""Tests for stackdiff.diff_pinner."""
import pytest

from stackdiff.diff_engine import DiffResult
from stackdiff.diff_pinner import (
    compare_to_pin,
    delete_pin,
    list_pins,
    load_pin,
    pin_diff,
)


@pytest.fixture()
def pin_dir(tmp_path):
    return str(tmp_path / "pins")


@pytest.fixture()
def sample_result():
    return DiffResult(
        removed={"db.host": "old-host"},
        added={"cache.url": "redis://new"},
        changed={"app.port": ["8080", "9090"]},
    )


def test_pin_diff_creates_file(pin_dir, sample_result):
    pinned = pin_diff(sample_result, "v1", pin_dir=pin_dir)
    assert pinned.label == "v1"
    pins = list_pins(pin_dir=pin_dir)
    assert "v1" in pins


def test_pin_diff_returns_pinned_diff(pin_dir, sample_result):
    pinned = pin_diff(sample_result, "release-1", pin_dir=pin_dir)
    assert pinned.removed == {"db.host": "old-host"}
    assert pinned.added == {"cache.url": "redis://new"}
    assert pinned.changed == {"app.port": ["8080", "9090"]}


def test_load_pin_returns_pinned_diff(pin_dir, sample_result):
    pin_diff(sample_result, "v2", pin_dir=pin_dir)
    loaded = load_pin("v2", pin_dir=pin_dir)
    assert loaded.label == "v2"
    assert loaded.removed == sample_result.removed
    assert loaded.added == sample_result.added


def test_load_pin_missing_raises(pin_dir):
    with pytest.raises(FileNotFoundError, match="no-such"):
        load_pin("no-such", pin_dir=pin_dir)


def test_list_pins_empty_dir(pin_dir):
    assert list_pins(pin_dir=pin_dir) == []


def test_list_pins_returns_all_labels(pin_dir, sample_result):
    pin_diff(sample_result, "alpha", pin_dir=pin_dir)
    pin_diff(sample_result, "beta", pin_dir=pin_dir)
    labels = list_pins(pin_dir=pin_dir)
    assert "alpha" in labels
    assert "beta" in labels


def test_delete_pin_removes_entry(pin_dir, sample_result):
    pin_diff(sample_result, "to-delete", pin_dir=pin_dir)
    removed = delete_pin("to-delete", pin_dir=pin_dir)
    assert removed is True
    assert "to-delete" not in list_pins(pin_dir=pin_dir)


def test_delete_pin_nonexistent_returns_false(pin_dir):
    assert delete_pin("ghost", pin_dir=pin_dir) is False


def test_compare_to_pin_no_deviation(pin_dir, sample_result):
    pin_diff(sample_result, "stable", pin_dir=pin_dir)
    report = compare_to_pin(sample_result, "stable", pin_dir=pin_dir)
    assert report["is_deviation"] is False
    assert report["new_removals"] == []
    assert report["new_additions"] == []


def test_compare_to_pin_detects_new_removal(pin_dir, sample_result):
    pin_diff(sample_result, "base", pin_dir=pin_dir)
    deviated = DiffResult(
        removed={"db.host": "old-host", "secret.key": "x"},
        added={"cache.url": "redis://new"},
        changed={"app.port": ["8080", "9090"]},
    )
    report = compare_to_pin(deviated, "base", pin_dir=pin_dir)
    assert report["is_deviation"] is True
    assert "secret.key" in report["new_removals"]


def test_compare_to_pin_detects_resolved_addition(pin_dir, sample_result):
    pin_diff(sample_result, "base2", pin_dir=pin_dir)
    resolved = DiffResult(
        removed={"db.host": "old-host"},
        added={},
        changed={"app.port": ["8080", "9090"]},
    )
    report = compare_to_pin(resolved, "base2", pin_dir=pin_dir)
    assert "cache.url" in report["resolved_additions"]


def test_pinned_diff_as_dict_has_all_keys(pin_dir, sample_result):
    pinned = pin_diff(sample_result, "dict-test", pin_dir=pin_dir)
    d = pinned.as_dict()
    for key in ("label", "removed", "added", "changed", "pinned_at"):
        assert key in d
