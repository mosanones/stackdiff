"""Tests for stackdiff.reporter."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from stackdiff.diff_engine import DiffResult
from stackdiff.reporter import build_report, generate_report, write_report


@pytest.fixture()
def no_diff() -> DiffResult:
    return DiffResult(added={}, removed={}, changed={})


@pytest.fixture()
def with_diff() -> DiffResult:
    return DiffResult(
        added={"NEW_KEY": "value"},
        removed={"OLD_KEY": "gone"},
        changed={"HOST": ("localhost", "prod.example.com")},
    )


def test_build_report_text_no_diff(no_diff: DiffResult) -> None:
    report = build_report(no_diff, fmt="text")
    assert "No differences" in report


def test_build_report_text_with_diff(with_diff: DiffResult) -> None:
    report = build_report(with_diff, fmt="text", label_a="staging", label_b="prod")
    assert "NEW_KEY" in report
    assert "OLD_KEY" in report
    assert "HOST" in report


def test_build_report_json_structure(with_diff: DiffResult) -> None:
    report = build_report(with_diff, fmt="json")
    data = json.loads(report)
    assert "added" in data
    assert "removed" in data
    assert "changed" in data
    assert data["added"]["NEW_KEY"] == "value"


def test_write_report_stdout(capsys, no_diff: DiffResult) -> None:
    report = build_report(no_diff)
    write_report(report)
    captured = capsys.readouterr()
    assert "No differences" in captured.out


def test_write_report_to_file_text(tmp_path: Path, with_diff: DiffResult) -> None:
    out = tmp_path / "report.txt"
    report = build_report(with_diff, fmt="text")
    write_report(report, output_path=str(out), fmt="text")
    content = out.read_text()
    assert "NEW_KEY" in content


def test_write_report_to_file_json(tmp_path: Path, with_diff: DiffResult) -> None:
    out = tmp_path / "sub" / "report.json"
    report = build_report(with_diff, fmt="json")
    write_report(report, output_path=str(out), fmt="json")
    data = json.loads(out.read_text())
    assert data["removed"]["OLD_KEY"] == "gone"


def test_generate_report_returns_string(no_diff: DiffResult) -> None:
    result = generate_report(no_diff, fmt="text")
    assert isinstance(result, str)


def test_generate_report_writes_file(tmp_path: Path, with_diff: DiffResult) -> None:
    out = tmp_path / "out.json"
    generate_report(with_diff, fmt="json", output_path=str(out))
    assert out.exists()
    data = json.loads(out.read_text())
    assert "changed" in data
