"""Integration tests for the run_pipeline function."""
import json
import os
import pytest
from stackdiff.pipeline import run_pipeline
from stackdiff.diff_engine import has_diff


@pytest.fixture()
def yaml_pair(tmp_path):
    a = tmp_path / "staging.yaml"
    b = tmp_path / "production.yaml"
    a.write_text("db_host: localhost\ndb_pass: secret\napp_env: staging\n")
    b.write_text("db_host: prod-db\ndb_pass: topsecret\napp_env: production\n")
    return str(a), str(b)


@pytest.fixture()
def identical_pair(tmp_path):
    a = tmp_path / "a.yaml"
    b = tmp_path / "b.yaml"
    content = "key1: value1\nkey2: value2\n"
    a.write_text(content)
    b.write_text(content)
    return str(a), str(b)


def test_pipeline_detects_diff(yaml_pair):
    path_a, path_b = yaml_pair
    result = run_pipeline(path_a, path_b)
    assert has_diff(result)


def test_pipeline_no_diff_identical(identical_pair):
    path_a, path_b = identical_pair
    result = run_pipeline(path_a, path_b)
    assert not has_diff(result)


def test_pipeline_masks_sensitive(yaml_pair):
    path_a, path_b = yaml_pair
    result = run_pipeline(path_a, path_b, mask=True)
    db_pass_diff = result.diffs.get("db_pass", {})
    assert db_pass_diff.get("value_a") == "***"
    assert db_pass_diff.get("value_b") == "***"


def test_pipeline_no_mask_exposes_values(yaml_pair):
    path_a, path_b = yaml_pair
    result = run_pipeline(path_a, path_b, mask=False)
    db_pass_diff = result.diffs.get("db_pass", {})
    assert db_pass_diff.get("value_a") == "secret"


def test_pipeline_include_filter(yaml_pair):
    path_a, path_b = yaml_pair
    result = run_pipeline(path_a, path_b, include=["app_env"], mask=False)
    assert "app_env" in result.diffs
    assert "db_host" not in result.diffs


def test_pipeline_keys_sorted(yaml_pair):
    path_a, path_b = yaml_pair
    result = run_pipeline(path_a, path_b, sort_mode="key")
    keys = list(result.diffs.keys())
    assert keys == sorted(keys)


def test_pipeline_labels_preserved(yaml_pair):
    path_a, path_b = yaml_pair
    result = run_pipeline(path_a, path_b, label_a="staging", label_b="prod")
    assert result.label_a == "staging"
    assert result.label_b == "prod"
