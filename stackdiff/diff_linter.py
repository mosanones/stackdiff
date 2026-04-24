"""diff_linter.py — lint a diff result against configurable rules.

Rules check for common anti-patterns such as empty values, all-caps keys
that look like unresolved placeholders, and values that differ only in
whitespace.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from stackdiff.diff_engine import DiffResult


@dataclass
class LintViolation:
    key: str
    rule: str
    message: str
    severity: str = "warning"  # "warning" | "error"

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "rule": self.rule,
            "message": self.message,
            "severity": self.severity,
        }


@dataclass
class LintReport:
    violations: List[LintViolation] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(v.severity == "error" for v in self.violations)

    @property
    def error_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == "warning")

    def as_dict(self) -> dict:
        return {
            "violations": [v.as_dict() for v in self.violations],
            "error_count": self.error_count,
            "warning_count": self.warning_count,
        }


def _check_empty_value(key: str, value: Optional[str]) -> Optional[LintViolation]:
    if value is not None and str(value).strip() == "":
        return LintViolation(
            key=key,
            rule="empty_value",
            message=f"Key '{key}' has an empty string value.",
            severity="warning",
        )
    return None


def _check_placeholder(key: str, value: Optional[str]) -> Optional[LintViolation]:
    if value is not None and str(value).startswith("<") and str(value).endswith(">"):
        return LintViolation(
            key=key,
            rule="placeholder_value",
            message=f"Key '{key}' looks like an unresolved placeholder: {value!r}.",
            severity="error",
        )
    return None


def _check_whitespace_only_diff(
    key: str, old: Optional[str], new: Optional[str]
) -> Optional[LintViolation]:
    if old is not None and new is not None:
        if str(old).strip() == str(new).strip() and old != new:
            return LintViolation(
                key=key,
                rule="whitespace_only_diff",
                message=(
                    f"Key '{key}' differs only in surrounding whitespace."
                ),
                severity="warning",
            )
    return None


def lint_diff(result: DiffResult) -> LintReport:
    """Run all lint rules against a DiffResult and return a LintReport."""
    violations: List[LintViolation] = []

    for key, old_val in result.removed.items():
        for check in (_check_empty_value(key, old_val), _check_placeholder(key, old_val)):
            if check:
                violations.append(check)

    for key, new_val in result.added.items():
        for check in (_check_empty_value(key, new_val), _check_placeholder(key, new_val)):
            if check:
                violations.append(check)

    for key, (old_val, new_val) in result.changed.items():
        for check in (
            _check_empty_value(key, new_val),
            _check_placeholder(key, new_val),
            _check_whitespace_only_diff(key, old_val, new_val),
        ):
            if check:
                violations.append(check)

    return LintReport(violations=violations)
