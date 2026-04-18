"""Tests for stackdiff.schedule_handler."""

import os
import time
import yaml
import pytest
from stackdiff.schedule_handler import start_scheduled_diff, stop_scheduled_diff


@pytest.fixture
def yaml_pair(tmp_path):
    a = tmp_path / "a.yaml"
    b = tmp_path / "b.yaml"
    a.write_text(yaml.dump({"host": "localhost", "port": 8080}))
    b.write_text(yaml.dump({"host": "prod.example.com", "port": 443}))
    return str(a), str(b)


def test_start_returns_state(yaml_pair):
    a, b = yaml_pair
    state = start_scheduled_diff(a, b, interval=60, max_runs=1)
    time.sleep(0.3)
    stop_scheduled_diff(state)
    assert state.runs >= 1


def test_scheduled_diff_runs_multiple_times(yaml_pair):
    a, b = yaml_pair
    state = start_scheduled_diff(a, b, interval=0, max_runs=3)
    time.sleep(0.5)
    stop_scheduled_diff(state)
    assert state.runs == 3


def test_error_handler_called_on_bad_files(tmp_path):
    errors = []
    state = start_scheduled_diff(
        str(tmp_path / "missing_a.yaml"),
        str(tmp_path / "missing_b.yaml"),
        interval=0,
        max_runs=2,
        on_error=errors.append,
    )
    time.sleep(0.3)
    stop_scheduled_diff(state)
    assert len(errors) >= 1


def test_stop_halts_execution(yaml_pair):
    a, b = yaml_pair
    state = start_scheduled_diff(a, b, interval=30)
    stop_scheduled_diff(state)
    assert not state.running
