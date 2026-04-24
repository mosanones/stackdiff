"""Tests for stackdiff.diff_linter."""
import pytest
from stackdiff.diff_engine import DiffResult
from stackdiff.diff_linter import (
    LintReport,
    LintViolation,
    lint_diff,
    _check_empty_value,
    _check_placeholder,
    _check_whitespace_only_diff,
)


@pytest.fixture
def clean_diff() -> DiffResult:
    return DiffResult(removed={}, added={}, changed={})


@pytest.fixture
def dirty_diff() -> DiffResult:
    return DiffResult(
        removed={"old_key": "old_value"},
        added={"new_key": "<REPLACE_ME>"},
        changed={
            "db.host": ("localhost", "db.prod.internal"),
            "app.name": ("my app ", " my app"),  # whitespace-only diff
            "api.secret": ("abc", ""),            # empty new value
        },
    )


# --- unit helpers ---

def test_check_empty_value_triggers_on_blank():
    v = _check_empty_value("some.key", "   ")
    assert v is not None
    assert v.rule == "empty_value"
    assert v.severity == "warning"


def test_check_empty_value_none_on_normal_value():
    assert _check_empty_value("some.key", "hello") is None


def test_check_empty_value_none_when_value_is_none():
    assert _check_empty_value("some.key", None) is None


def test_check_placeholder_triggers():
    v = _check_placeholder("token", "<YOUR_TOKEN>")
    assert v is not None
    assert v.rule == "placeholder_value"
    assert v.severity == "error"


def test_check_placeholder_none_on_real_value():
    assert _check_placeholder("token", "abc123") is None


def test_check_whitespace_only_diff_triggers():
    v = _check_whitespace_only_diff("app.name", "hello ", " hello")
    assert v is not None
    assert v.rule == "whitespace_only_diff"
    assert v.severity == "warning"


def test_check_whitespace_only_diff_none_on_real_change():
    assert _check_whitespace_only_diff("app.name", "hello", "world") is None


def test_check_whitespace_only_diff_none_when_identical():
    assert _check_whitespace_only_diff("x", "same", "same") is None


# --- lint_diff integration ---

def test_lint_diff_clean_returns_empty_report(clean_diff):
    report = lint_diff(clean_diff)
    assert isinstance(report, LintReport)
    assert report.violations == []
    assert not report.has_errors


def test_lint_diff_detects_placeholder_in_added(dirty_diff):
    report = lint_diff(dirty_diff)
    rules = [v.rule for v in report.violations]
    assert "placeholder_value" in rules


def test_lint_diff_detects_empty_value_in_changed(dirty_diff):
    report = lint_diff(dirty_diff)
    rules = [v.rule for v in report.violations]
    assert "empty_value" in rules


def test_lint_diff_detects_whitespace_only_diff(dirty_diff):
    report = lint_diff(dirty_diff)
    rules = [v.rule for v in report.violations]
    assert "whitespace_only_diff" in rules


def test_lint_diff_has_errors_when_placeholder_present(dirty_diff):
    report = lint_diff(dirty_diff)
    assert report.has_errors
    assert report.error_count >= 1


def test_lint_report_as_dict(dirty_diff):
    report = lint_diff(dirty_diff)
    d = report.as_dict()
    assert "violations" in d
    assert "error_count" in d
    assert "warning_count" in d
    assert isinstance(d["violations"], list)


def test_violation_as_dict():
    v = LintViolation(key="x", rule="test_rule", message="msg", severity="error")
    d = v.as_dict()
    assert d == {"key": "x", "rule": "test_rule", "message": "msg", "severity": "error"}
