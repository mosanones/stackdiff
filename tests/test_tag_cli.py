import json
import pytest
from unittest.mock import patch, MagicMock
from stackdiff.tag_cli import main, build_tag_parser
from stackdiff.diff_tags import TaggedDiff, TaggedKey
from stackdiff.differ import DiffContext
from stackdiff.diff_engine import DiffResult


@pytest.fixture
def mock_ctx():
    diff = MagicMock(spec=DiffResult)
    diff.changed = {"db_host": ("old", "new"), "api_key": ("x", "y"), "app_name": ("a", "b")}
    ctx = MagicMock(spec=DiffContext)
    ctx.diff = diff
    return ctx


def test_build_tag_parser_returns_parser():
    p = build_tag_parser()
    assert p is not None


def test_main_text_output(mock_ctx, capsys):
    with patch("stackdiff.tag_cli.diff_files", return_value=mock_ctx):
        main(["staging.yaml", "prod.yaml"])
    out = capsys.readouterr().out
    assert "db_host" in out


def test_main_json_output(mock_ctx, capsys):
    with patch("stackdiff.tag_cli.diff_files", return_value=mock_ctx):
        main(["staging.yaml", "prod.yaml", "--format", "json"])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "tagged_keys" in data
    assert "tag_index" in data


def test_main_filter_by_tag_text(mock_ctx, capsys):
    with patch("stackdiff.tag_cli.diff_files", return_value=mock_ctx):
        main(["staging.yaml", "prod.yaml", "--tag", "database"])
    out = capsys.readouterr().out
    assert "database" in out


def test_main_filter_by_tag_json(mock_ctx, capsys):
    with patch("stackdiff.tag_cli.diff_files", return_value=mock_ctx):
        main(["staging.yaml", "prod.yaml", "--tag", "auth", "--format", "json"])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["tag"] == "auth"
    assert "api_key" in data["keys"]


def test_main_missing_tag_text(mock_ctx, capsys):
    with patch("stackdiff.tag_cli.diff_files", return_value=mock_ctx):
        main(["staging.yaml", "prod.yaml", "--tag", "nonexistent"])
    out = capsys.readouterr().out
    assert "No keys" in out


def test_main_no_changed_keys(capsys):
    diff = MagicMock(spec=DiffResult)
    diff.changed = {}
    ctx = MagicMock(spec=DiffContext)
    ctx.diff = diff
    with patch("stackdiff.tag_cli.diff_files", return_value=ctx):
        main(["staging.yaml", "prod.yaml"])
    out = capsys.readouterr().out
    assert "No changed keys" in out
