"""Tests for stackdiff.differ module."""
import json
import os
import pytest

from stackdiff.differ import diff_files, diff_against_snapshot, DiffContext
from stackdiff.snapshotter import save_snapshot


@pytest.fixture()
def yaml_pair(tmp_path):
    left = tmp_path / "staging.yaml"
    right = tmp_path / "prod.yaml"
    left.write_text("DB_HOST: staging-db\nSECRET_KEY: abc123\nDEBUG: true\n")
    right.write_text("DB_HOST: prod-db\nSECRET_KEY: xyz789\nDEBUG: false\n")
    return str(left), str(right)


@pytest.fixture()
def snap_dir(tmp_path):
    d = tmp_path / "snaps"
    d.mkdir()
    return str(d)


def test_diff_files_returns_context(yaml_pair):
    left, right = yaml_pair
    ctx = diff_files(left, right, left_label="staging", right_label="prod")
    assert isinstance(ctx, DiffContext)
    assert ctx.left_label == "staging"
    assert ctx.right_label == "prod"


def test_diff_files_detects_changes(yaml_pair):
    left, right = yaml_pair
    ctx = diff_files(left, right, mask=False)
    assert ctx.result.has_diff()


def test_diff_files_masks_secrets(yaml_pair):
    left, right = yaml_pair
    ctx = diff_files(left, right, mask=True)
    for entry in ctx.result.changed:
        if entry.key == "SECRET_KEY":
            assert entry.left_value == "***"
            assert entry.right_value == "***"


def test_diff_files_include_filter(yaml_pair):
    left, right = yaml_pair
    ctx = diff_files(left, right, include=["DB_HOST"], mask=False)
    keys = {e.key for e in ctx.result.changed}
    assert "DB_HOST" in keys
    assert "DEBUG" not in keys


def test_diff_against_snapshot(yaml_pair, snap_dir):
    left, _ = yaml_pair
    from stackdiff.config_loader import load_config
    cfg = load_config(left)
    save_snapshot(cfg, "v1", snap_dir=snap_dir)

    ctx = diff_against_snapshot(left, tag="v1", snap_dir=snap_dir, mask=False)
    assert isinstance(ctx, DiffContext)
    assert ctx.baseline_used is True
    assert ctx.snapshot_tag == "v1"
    assert not ctx.result.has_diff()


def test_diff_against_snapshot_detects_change(yaml_pair, snap_dir):
    left, right = yaml_pair
    from stackdiff.config_loader import load_config
    baseline = load_config(left)
    save_snapshot(baseline, "v1", snap_dir=snap_dir)

    ctx = diff_against_snapshot(right, tag="v1", label="prod", snap_dir=snap_dir, mask=False)
    assert ctx.result.has_diff()
