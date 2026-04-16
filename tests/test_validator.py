"""Tests for stackdiff.validator."""

import pytest
from stackdiff.validator import (
    ValidationResult,
    check_required_keys,
    check_type_consistency,
    validate,
)


@pytest.fixture
def base_cfg():
    return {"db.host": "localhost", "db.port": 5432, "app.debug": False}


@pytest.fixture
def compare_cfg():
    return {"db.host": "prod-host", "db.port": 5432, "app.debug": False}


def test_check_required_keys_all_present(compare_cfg):
    missing = check_required_keys(compare_cfg, ["db.host", "db.port"])
    assert missing == []


def test_check_required_keys_some_missing(compare_cfg):
    missing = check_required_keys(compare_cfg, ["db.host", "app.secret"])
    assert "app.secret" in missing
    assert "db.host" not in missing


def test_check_required_keys_empty_required(compare_cfg):
    assert check_required_keys(compare_cfg, []) == []


def test_check_type_consistency_no_mismatch(base_cfg, compare_cfg):
    mismatches = check_type_consistency(base_cfg, compare_cfg)
    assert mismatches == []


def test_check_type_consistency_detects_mismatch(base_cfg):
    compare = {"db.host": "prod", "db.port": "5432", "app.debug": False}
    mismatches = check_type_consistency(base_cfg, compare)
    assert "db.port" in mismatches


def test_check_type_consistency_ignores_missing_in_compare(base_cfg):
    compare = {"db.host": "prod"}
    mismatches = check_type_consistency(base_cfg, compare)
    assert mismatches == []


def test_validate_valid(base_cfg, compare_cfg):
    result = validate(base_cfg, compare_cfg, required_keys=["db.host"])
    assert result.valid is True
    assert result.errors == []


def test_validate_missing_required(base_cfg, compare_cfg):
    result = validate(base_cfg, compare_cfg, required_keys=["db.host", "app.secret"])
    assert result.valid is False
    assert any("app.secret" in e for e in result.errors)


def test_validate_type_mismatch(base_cfg):
    compare = {"db.host": "prod", "db.port": "5432", "app.debug": False}
    result = validate(base_cfg, compare)
    assert result.valid is False
    assert any("db.port" in e for e in result.errors)


def test_validation_result_no_required_keys(base_cfg, compare_cfg):
    result = validate(base_cfg, compare_cfg)
    assert result.valid is True
