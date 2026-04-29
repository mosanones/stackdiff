"""Tests for stackdiff.diff_summarizer_cli."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from stackdiff.diff_summarizer_cli import build_summarizer_parser, main


@pytest.fixture()
def yaml_pair(tmp_path: Path):
    left = tmp_path / "left.yaml"
    right = tmp_path / "right.yaml"
    left.write_text("db_host: localhost\ndb_password: secret\napp_port: 8080\n")
    right.write_text("db_host: prod-db\ndb_password: topsecret\napp_port: 8080\n")
    return str(left), str(right)


@pytest.fixture()
def identical_pair(tmp_path: Path):
    left = tmp_path / "a.yaml"
    right = tmp_path / "b.yaml"
    left.write_text("key: value\n")
    right.write_text("key: value\n")
    return str(left), str(right)


def test_build_summarizer_parser_returns_parser():
    parser = build_summarizer_parser()
    assert parser is not None
    assert parser.prog == "stackdiff-summary"


def test_main_text_output_contains_summary(yaml_pair, capsys):
    left, right = yaml_pair
    main([left, right, "--format", "text"])
    captured = capsys.readouterr()
    assert "Summary:" in captured.out
    assert "Total changes" in captured.out


def test_main_json_output_is_valid_json(yaml_pair, capsys):
    left, right = yaml_pair
    main([left, right, "--format", "json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "score" in data
    assert "total_changes" in data
    assert "label" in data


def test_main_text_shows_critical_keys(yaml_pair, capsys):
    left, right = yaml_pair
    main([left, right])
    captured = capsys.readouterr()
    # db_password should be flagged as critical
    assert "Critical" in captured.out


def test_main_no_diff_clean_label(identical_pair, capsys):
    left, right = identical_pair
    main([left, right, "--format", "json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["total_changes"] == 0
    assert data["label"] == "clean"


def test_main_fail_on_critical_exits_2(yaml_pair):
    left, right = yaml_pair
    with pytest.raises(SystemExit) as exc_info:
        main([left, right, "--fail-on-critical"])
    assert exc_info.value.code == 2


def test_main_fail_on_critical_no_exit_when_clean(identical_pair):
    left, right = identical_pair
    # Should not raise
    main([left, right, "--fail-on-critical"])


def test_main_custom_labels(yaml_pair, capsys):
    left, right = yaml_pair
    main([left, right, "--label-left", "staging", "--label-right", "prod", "--format", "text"])
    captured = capsys.readouterr()
    assert "Summary:" in captured.out
