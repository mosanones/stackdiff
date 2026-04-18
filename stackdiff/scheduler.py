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
