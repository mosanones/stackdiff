"""Scheduled diff runs with configurable intervals and persistence."""

import time
import threading
from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass
class ScheduleConfig:
    interval_seconds: int
    label: str = "default"
    max_runs: Optional[int] = None
    on_diff: Optional[Callable] = None
    on_error: Optional[Callable] = None


@dataclass
class ScheduleState:
    runs: int = 0
    errors: int = 0
    last_run: Optional[float] = None
    running: bool = False
    _thread: Optional[threading.Thread] = field(default=None, repr=False)


def _run_loop(job: Callable, config: ScheduleConfig, state: ScheduleState) -> None:
    while state.running:
        try:
            job()
            state.runs += 1
            state.last_run = time.time()
        except Exception as exc:
            state.errors += 1
            if config.on_error:
                config.on_error(exc)
        if config.max_runs and state.runs >= config.max_runs:
            state.running = False
            break
        time.sleep(config.interval_seconds)


def start_scheduler(job: Callable, config: ScheduleConfig) -> ScheduleState:
    state = ScheduleState(running=True)
    t = threading.Thread(target=_run_loop, args=(job, config, state), daemon=True)
    state._thread = t
    t.start()
    return state


def stop_scheduler(state: ScheduleState) -> None:
    state.running = False
    if state._thread:
        state._thread.join(timeout=5)


def scheduler_status(state: ScheduleState) -> dict:
    """Return a summary of the scheduler's current state.

    Returns a plain dict suitable for logging or display, including
    whether the scheduler is active, run/error counts, and the time
    elapsed since the last run.
    """
    elapsed = None
    if state.last_run is not None:
        elapsed = round(time.time() - state.last_run, 2)
    return {
        "running": state.running,
        "runs": state.runs,
        "errors": state.errors,
        "last_run": state.last_run,
        "seconds_since_last_run": elapsed,
    }


def wait_for_run(state: ScheduleState, timeout: float = 10.0, poll_interval: float = 0.1) -> bool:
    """Block until at least one run has completed or the timeout expires.

    Useful in tests or CLI tools that need to wait for the scheduler to
    perform its first job execution before proceeding.

    Returns True if a run was observed within the timeout, False otherwise.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        if state.runs > 0:
            return True
        time.sleep(poll_interval)
    return False
