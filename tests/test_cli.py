"""Tests for stackdiff.cli."""
import json
import os
import textwrap
import pytest
from stackdiff.cli import main


@pytest.fixture
def yaml_files(tmp_path):
    staging = tmp_path / "staging.yaml"
    prod = tmp_path / "prod.yaml"
    staging.write_text(textwrap.dedent("""\
        db:
          host: staging-db
          port: 5432
        debug: true
    """))
    prod.write_text(textwrap.dedent("""\
        db:
          host: prod-db
          port: 5432
        log_level: warn
    """))
    return str(staging), str(prod)


def test_cli_no_diff_exit_zero(tmp_path):
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text("key: value\n")
    code = main([str(cfg), str(cfg), "--no-color"])
    assert code == 0


def test_cli_diff_exit_zero_without_flag(yaml_files, capsys):
    staging, prod = yaml_files
    code = main([staging, prod, "--no-color"])
    assert code == 0


def test_cli_diff_exit_one_with_flag(yaml_files):
    staging, prod = yaml_files
    code = main([staging, prod, "--no-color", "--exit-code"])
    assert code == 1


def test_cli_json_output(yaml_files, capsys):
    staging, prod = yaml_files
    main([staging, prod, "--format", "json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "changed" in data


def test_cli_custom_labels(yaml_files, capsys):
    staging, prod = yaml_files
    main([staging, prod, "--no-color", "--left-label", "STG", "--right-label", "PRD"])
    captured = capsys.readouterr()
    assert "STG" in captured.out
    assert "PRD" in captured.out


def test_cli_missing_file(tmp_path, capsys):
    code = main([str(tmp_path / "missing.yaml"), str(tmp_path / "also.yaml")])
    assert code == 2
