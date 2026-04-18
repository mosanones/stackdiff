"""Tests for stackdiff.scheduler."""

import time
import pytest
from stackdiff.scheduler import ScheduleConfig, start_scheduler, stop_scheduler


def test_scheduler_runs_job():
    calls = []
    config = ScheduleConfig(interval_seconds=0, max_runs=3)
    state = start_scheduler(lambda: calls.append(1), config)
    time.sleep(0.3)
    stop_scheduler(state)
    assert len(calls) >= 3


def test_scheduler_stops_after_max_runs():
    calls = []
    config = ScheduleConfig(interval_seconds=0, max_runs=2)
    state = start_scheduler(lambda: calls.append(1), config)
    time.sleep(0.3)
    assert state.runs == 2
    assert not state.running


def test_scheduler_records_errors():
    def bad_job():
        raise ValueError("boom")

    errors_seen = []
    config = ScheduleConfig(interval_seconds=0, max_runs=2, on_error=errors_seen.append)
    state = start_scheduler(bad_job, config)
    time.sleep(0.3)
    stop_scheduler(state)
    assert state.errors >= 1
    assert isinstance(errors_seen[0], ValueError)


def test_stop_scheduler_sets_running_false():
    config = ScheduleConfig(interval_seconds=10)
    state = start_scheduler(lambda: None, config)
    stop_scheduler(state)
    assert not state.running


def test_last_run_updated():
    config = ScheduleConfig(interval_seconds=0, max_runs=1)
    state = start_scheduler(lambda: None, config)
    time.sleep(0.3)
    assert state.last_run is not None
