"""Tests for stackdiff.masker."""

import pytest
from stackdiff.masker import mask_config, mask_diff_values, MASK_VALUE


@pytest.fixture
def flat_cfg():
    return {
        "app.name": "myapp",
        "app.version": "1.2.3",
        "db.password": "s3cr3t",
        "auth.api_key": "abc123",
        "jwt.secret": "topsecret",
        "service.token": "tok999",
        "log.level": "info",
    }


def test_mask_config_hides_sensitive(flat_cfg):
    result = mask_config(flat_cfg)
    assert result["db.password"] == MASK_VALUE
    assert result["auth.api_key"] == MASK_VALUE
    assert result["jwt.secret"] == MASK_VALUE
    assert result["service.token"] == MASK_VALUE


def test_mask_config_keeps_safe_values(flat_cfg):
    result = mask_config(flat_cfg)
    assert result["app.name"] == "myapp"
    assert result["app.version"] == "1.2.3"
    assert result["log.level"] == "info"


def test_mask_config_does_not_mutate_original(flat_cfg):
    original_password = flat_cfg["db.password"]
    mask_config(flat_cfg)
    assert flat_cfg["db.password"] == original_password


def test_mask_config_custom_patterns():
    cfg = {"db.host": "localhost", "db.password": "s3cr3t"}
    result = mask_config(cfg, patterns=[r".*host.*"])
    assert result["db.host"] == MASK_VALUE
    assert result["db.password"] == "s3cr3t"  # default patterns not active


def test_mask_config_extra_patterns(flat_cfg):
    result = mask_config(flat_cfg, extra_patterns=[r".*name.*"])
    assert result["app.name"] == MASK_VALUE
    assert result["db.password"] == MASK_VALUE  # defaults still active


def test_mask_diff_values_masks_all_buckets():
    added = {"auth.token": "new_tok", "app.name": "myapp"}
    removed = {"db.password": "old_pass", "log.level": "debug"}
    changed = {
        "jwt.secret": ("old_secret", "new_secret"),
        "app.version": ("1.0", "2.0"),
    }

    m_added, m_removed, m_changed = mask_diff_values(added, removed, changed)

    assert m_added["auth.token"] == MASK_VALUE
    assert m_added["app.name"] == "myapp"

    assert m_removed["db.password"] == MASK_VALUE
    assert m_removed["log.level"] == "debug"

    assert m_changed["jwt.secret"] == (MASK_VALUE, MASK_VALUE)
    assert m_changed["app.version"] == ("1.0", "2.0")


def test_mask_diff_values_empty_buckets():
    m_added, m_removed, m_changed = mask_diff_values({}, {}, {})
    assert m_added == {}
    assert m_removed == {}
    assert m_changed == {}
