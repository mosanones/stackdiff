"""Tests for diff_snapshot_diff and snapshot_diff_cli."""
from __future__ import annotations

import json
import pytest

from stackdiff.snapshotter import save_snapshot
from stackdiff.diff_snapshot_diff import compare_snapshots, list_comparable_snapshots, SnapshotComparison
from stackdiff.snapshot_diff_cli import build_snapshot_diff_parser, main


@pytest.fixture()
def snap_dir(tmp_path):
    return str(tmp_path / "snaps")


@pytest.fixture()
def two_snaps(snap_dir):
    cfg_a = {"db.host": "localhost", "app.debug": "false", "api.key": "secret"}
    cfg_b = {"db.host": "prod-db", "app.debug": "false", "api.key": "secret2"}
    save_snapshot("staging", cfg_a, snapshot_dir=snap_dir)
    save_snapshot("production", cfg_b, snapshot_dir=snap_dir)
    return snap_dir


@pytest.fixture()
def identical_snaps(snap_dir):
    cfg = {"db.host": "localhost", "app.debug": "true"}
    save_snapshot("snap_a", cfg, snapshot_dir=snap_dir)
    save_snapshot("snap_b", cfg, snapshot_dir=snap_dir)
    return snap_dir


def test_compare_snapshots_returns_snapshot_comparison(two_snaps):
    result = compare_snapshots("staging", "production", snapshot_dir=two_snaps)
    assert isinstance(result, SnapshotComparison)


def test_compare_snapshots_detects_changed_key(two_snaps):
    result = compare_snapshots("staging", "production", snapshot_dir=two_snaps)
    assert result.diff.has_diff()
    assert "db.host" in result.diff.changed


def test_compare_snapshots_no_diff_identical(identical_snaps):
    result = compare_snapshots("snap_a", "snap_b", snapshot_dir=identical_snaps)
    assert not result.diff.has_diff()


def test_compare_snapshots_masks_secrets_by_default(two_snaps):
    result = compare_snapshots("staging", "production", snapshot_dir=two_snaps, mask_secrets=True)
    assert result.masked is True
    # api.key values should be masked — not appear as raw secrets
    for key, (old, new) in result.diff.changed.items():
        if "key" in key.lower() or "secret" in key.lower():
            assert "secret" not in str(old).lower() or old == "***"


def test_compare_snapshots_no_mask_flag(two_snaps):
    result = compare_snapshots("staging", "production", snapshot_dir=two_snaps, mask_secrets=False)
    assert result.masked is False


def test_as_dict_has_expected_keys(two_snaps):
    result = compare_snapshots("staging", "production", snapshot_dir=two_snaps)
    d = result.as_dict()
    for key in ("left_name", "right_name", "has_diff", "added", "removed", "changed", "score", "masked"):
        assert key in d


def test_list_comparable_snapshots(two_snaps):
    names = list_comparable_snapshots(snapshot_dir=two_snaps)
    assert "staging" in names
    assert "production" in names


def test_list_comparable_snapshots_empty(snap_dir):
    names = list_comparable_snapshots(snapshot_dir=snap_dir)
    assert names == []


# --- CLI tests ---

def test_build_snapshot_diff_parser_returns_parser():
    parser = build_snapshot_diff_parser()
    assert parser is not None


def test_cli_text_output(two_snaps, capsys):
    main(["staging", "production", "--snapshot-dir", two_snaps])
    captured = capsys.readouterr()
    assert "Risk score" in captured.out


def test_cli_json_output(two_snaps, capsys):
    main(["staging", "production", "--snapshot-dir", two_snaps, "--format", "json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["left_name"] == "staging"
    assert data["right_name"] == "production"


def test_cli_fail_on_diff_exits_one(two_snaps):
    with pytest.raises(SystemExit) as exc_info:
        main(["staging", "production", "--snapshot-dir", two_snaps, "--fail-on-diff"])
    assert exc_info.value.code == 1


def test_cli_no_diff_no_exit(identical_snaps):
    # Should not raise SystemExit
    main(["snap_a", "snap_b", "--snapshot-dir", identical_snaps, "--fail-on-diff"])


def test_cli_list_flag(two_snaps, capsys):
    main(["--list", "--snapshot-dir", two_snaps, "placeholder", "placeholder"])
    captured = capsys.readouterr()
    assert "staging" in captured.out
    assert "production" in captured.out
