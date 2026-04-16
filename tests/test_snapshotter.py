"""Tests for stackdiff.snapshotter."""
import pytest
from stackdiff.snapshotter import (
    save_snapshot,
    load_snapshot,
    list_snapshots,
    delete_snapshot,
)


@pytest.fixture()
def snap_dir(tmp_path):
    return str(tmp_path / "snaps")


@pytest.fixture()
def sample_cfg():
    return {"app.debug": "true", "db.host": "localhost", "db.port": "5432"}


def test_save_creates_file(snap_dir, sample_cfg):
    path = save_snapshot(sample_cfg, "staging", snapshot_dir=snap_dir)
    assert path.exists()


def test_load_returns_config(snap_dir, sample_cfg):
    save_snapshot(sample_cfg, "staging", snapshot_dir=snap_dir)
    loaded = load_snapshot("staging", snapshot_dir=snap_dir)
    assert loaded == sample_cfg


def test_load_missing_raises(snap_dir):
    with pytest.raises(FileNotFoundError, match="no_such"):
        load_snapshot("no_such", snapshot_dir=snap_dir)


def test_list_snapshots_empty(snap_dir):
    assert list_snapshots(snapshot_dir=snap_dir) == []


def test_list_snapshots_multiple(snap_dir, sample_cfg):
    save_snapshot(sample_cfg, "staging", snapshot_dir=snap_dir)
    save_snapshot(sample_cfg, "production", snapshot_dir=snap_dir)
    labels = list_snapshots(snapshot_dir=snap_dir)
    assert "staging" in labels
    assert "production" in labels
    assert len(labels) == 2


def test_delete_existing(snap_dir, sample_cfg):
    save_snapshot(sample_cfg, "staging", snapshot_dir=snap_dir)
    result = delete_snapshot("staging", snapshot_dir=snap_dir)
    assert result is True
    assert list_snapshots(snapshot_dir=snap_dir) == []


def test_delete_nonexistent(snap_dir):
    assert delete_snapshot("ghost", snapshot_dir=snap_dir) is False


def test_save_includes_metadata(snap_dir, sample_cfg, tmp_path):
    import json
    path = save_snapshot(
        sample_cfg, "staging", snapshot_dir=snap_dir, metadata={"env": "ci"}
    )
    payload = json.loads(path.read_text())
    assert payload["metadata"]["env"] == "ci"
    assert "timestamp" in payload


def test_roundtrip_special_chars(snap_dir, sample_cfg):
    save_snapshot(sample_cfg, "my label", snapshot_dir=snap_dir)
    loaded = load_snapshot("my label", snapshot_dir=snap_dir)
    assert loaded == sample_cfg
