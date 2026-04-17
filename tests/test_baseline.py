"""Tests for stackdiff.baseline."""

import pytest
from pathlib import Path

from stackdiff.baseline import (
    save_baseline,
    load_baseline,
    list_baselines,
    delete_baseline,
    diff_against_baseline,
)


@pytest.fixture
def bdir(tmp_path):
    return tmp_path / "baselines"


@pytest.fixture
def sample_cfg():
    return {"db.host": "localhost", "db.port": "5432", "app.debug": "false"}


def test_save_creates_file(bdir, sample_cfg):
    path = save_baseline("prod", sample_cfg, bdir)
    assert path.exists()
    assert path.suffix == ".json"


def test_load_returns_config(bdir, sample_cfg):
    save_baseline("prod", sample_cfg, bdir)
    loaded = load_baseline("prod", bdir)
    assert loaded == sample_cfg


def test_load_missing_raises(bdir):
    with pytest.raises(FileNotFoundError, match="Baseline 'ghost' not found"):
        load_baseline("ghost", bdir)


def test_list_baselines_empty(bdir):
    assert list_baselines(bdir) == []


def test_list_baselines_multiple(bdir, sample_cfg):
    save_baseline("prod", sample_cfg, bdir)
    save_baseline("staging", sample_cfg, bdir)
    assert list_baselines(bdir) == ["prod", "staging"]


def test_delete_existing(bdir, sample_cfg):
    save_baseline("prod", sample_cfg, bdir)
    assert delete_baseline("prod", bdir) is True
    assert list_baselines(bdir) == []


def test_delete_missing(bdir):
    assert delete_baseline("ghost", bdir) is False


def test_diff_detects_removed(bdir, sample_cfg):
    save_baseline("prod", sample_cfg, bdir)
    current = {k: v for k, v in sample_cfg.items() if k != "db.host"}
    result = diff_against_baseline("prod", current, bdir)
    assert "db.host" in result["removed"]


def test_diff_detects_added(bdir, sample_cfg):
    save_baseline("prod", sample_cfg, bdir)
    current = {**sample_cfg, "app.new_key": "yes"}
    result = diff_against_baseline("prod", current, bdir)
    assert "app.new_key" in result["added"]


def test_diff_detects_changed(bdir, sample_cfg):
    save_baseline("prod", sample_cfg, bdir)
    current = {**sample_cfg, "db.port": "5433"}
    result = diff_against_baseline("prod", current, bdir)
    assert result["changed"]["db.port"] == {"baseline": "5432", "current": "5433"}


def test_diff_no_changes(bdir, sample_cfg):
    save_baseline("prod", sample_cfg, bdir)
    result = diff_against_baseline("prod", sample_cfg, bdir)
    assert result == {"removed": {}, "added": {}, "changed": {}}
