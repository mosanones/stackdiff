"""Tests for stackdiff.diff_sanitizer."""
from __future__ import annotations

import pytest

from stackdiff.diff_sanitizer import (
    SanitizeOptions,
    SanitizeResult,
    sanitize_config,
)


@pytest.fixture()
def raw_cfg():
    return {
        "db_host": "  localhost  ",
        "db_password": "secret",
        "api_url": "https://user:pass@api.example.com/v1",
        "debug": True,
        "timeout": None,
        "log_level": "INFO",
    }


def test_sanitize_returns_sanitize_result(raw_cfg):
    result = sanitize_config(raw_cfg)
    assert isinstance(result, SanitizeResult)


def test_strip_whitespace_default(raw_cfg):
    result = sanitize_config(raw_cfg)
    assert result.sanitized["db_host"] == "localhost"


def test_strip_whitespace_disabled(raw_cfg):
    opts = SanitizeOptions(strip_whitespace=False)
    result = sanitize_config(raw_cfg, opts)
    assert result.sanitized["db_host"] == "  localhost  "


def test_url_credentials_redacted(raw_cfg):
    result = sanitize_config(raw_cfg)
    assert "user:pass" not in result.sanitized["api_url"]
    assert "api_url" in result.redacted_keys


def test_url_credentials_redaction_disabled(raw_cfg):
    opts = SanitizeOptions(redact_url_credentials=False)
    result = sanitize_config(raw_cfg, opts)
    assert "user:pass" in result.sanitized["api_url"]
    assert "api_url" not in result.redacted_keys


def test_drop_null_values(raw_cfg):
    opts = SanitizeOptions(drop_null_values=True)
    result = sanitize_config(raw_cfg, opts)
    assert "timeout" not in result.sanitized
    assert "timeout" in result.dropped_keys


def test_null_kept_by_default(raw_cfg):
    result = sanitize_config(raw_cfg)
    assert "timeout" in result.sanitized
    assert result.sanitized["timeout"] is None


def test_lowercase_keys(raw_cfg):
    cfg = {"DB_HOST": "localhost", "API_KEY": "abc"}
    opts = SanitizeOptions(lowercase_keys=True)
    result = sanitize_config(cfg, opts)
    assert "db_host" in result.sanitized
    assert "api_key" in result.sanitized
    assert "DB_HOST" not in result.sanitized


def test_was_modified_true_when_redacted(raw_cfg):
    result = sanitize_config(raw_cfg)
    assert result.was_modified() is True


def test_was_modified_false_on_clean_config():
    cfg = {"host": "localhost", "port": "5432"}
    result = sanitize_config(cfg)
    assert result.was_modified() is False


def test_original_not_mutated(raw_cfg):
    original_url = raw_cfg["api_url"]
    sanitize_config(raw_cfg)
    assert raw_cfg["api_url"] == original_url


def test_as_dict_keys(raw_cfg):
    result = sanitize_config(raw_cfg)
    d = result.as_dict()
    assert "redacted_keys" in d
    assert "dropped_keys" in d
    assert "was_modified" in d


def test_extra_redact_patterns():
    cfg = {"token": "Bearer abc123secret"}
    opts = SanitizeOptions(extra_redact_patterns=[r"Bearer \S+"])
    result = sanitize_config(cfg, opts)
    assert "token" in result.redacted_keys


def test_non_string_values_unchanged():
    cfg = {"port": 5432, "enabled": False, "retries": 3}
    result = sanitize_config(cfg)
    assert result.sanitized["port"] == 5432
    assert result.sanitized["enabled"] is False
