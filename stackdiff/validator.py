"""Validate flattened configs for required keys and type consistency."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ValidationResult:
    valid: bool
    missing_keys: list[str] = field(default_factory=list)
    type_mismatches: list[str] = field(default_factory=list)

    @property
    def errors(self) -> list[str]:
        msgs = []
        for k in self.missing_keys:
            msgs.append(f"Missing required key: {k}")
        for k in self.type_mismatches:
            msgs.append(f"Type mismatch for key: {k}")
        return msgs


def check_required_keys(
    config: dict[str, Any], required: list[str]
) -> list[str]:
    """Return list of required keys absent from config."""
    return [k for k in required if k not in config]


def check_type_consistency(
    base: dict[str, Any], compare: dict[str, Any]
) -> list[str]:
    """Return keys where both configs have the key but types differ."""
    mismatches = []
    for k in base:
        if k in compare and type(base[k]) is not type(compare[k]):
            mismatches.append(k)
    return mismatches


def validate(
    base: dict[str, Any],
    compare: dict[str, Any],
    required_keys: list[str] | None = None,
) -> ValidationResult:
    """Run all validation checks and return a ValidationResult."""
    missing = check_required_keys(compare, required_keys or [])
    mismatches = check_type_consistency(base, compare)
    valid = not missing and not mismatches
    return ValidationResult(valid=valid, missing_keys=missing, type_mismatches=mismatches)
