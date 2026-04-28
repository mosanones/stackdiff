"""diff_watchdog.py — rate-limited alert watchdog for repeated diff runs.

Tracks how many times a diff result exceeds a risk threshold within a rolling
time window and fires a callback when the breach count crosses a limit.
"""
from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field
from typing import Callable, Deque, Optional

from stackdiff.scorer import DiffScore


@dataclass
class WatchdogConfig:
    """Configuration for the watchdog."""
    score_threshold: float = 40.0      # scores >= this are considered breaches
    window_seconds: float = 300.0      # rolling window size
    max_breaches: int = 3              # trigger after this many breaches in window
    cooldown_seconds: float = 60.0     # minimum gap between consecutive triggers


@dataclass
class WatchdogState:
    """Mutable runtime state for a watchdog instance."""
    breaches: Deque[float] = field(default_factory=deque)
    last_triggered: Optional[float] = None
    trigger_count: int = 0


def _prune_window(state: WatchdogState, window: float, now: float) -> None:
    """Remove breach timestamps that have fallen outside the rolling window."""
    cutoff = now - window
    while state.breaches and state.breaches[0] < cutoff:
        state.breaches.popleft()


def evaluate_watchdog(
    score: DiffScore,
    state: WatchdogState,
    config: WatchdogConfig,
    callback: Callable[[WatchdogState], None],
    *,
    _now: Optional[float] = None,
) -> bool:
    """Record a score observation; fire *callback* if the watchdog trips.

    Returns True when the callback was invoked, False otherwise.
    """
    now = _now if _now is not None else time.monotonic()

    _prune_window(state, config.window_seconds, now)

    if score.score >= config.score_threshold:
        state.breaches.append(now)

    if len(state.breaches) < config.max_breaches:
        return False

    # Enforce cooldown between triggers
    if state.last_triggered is not None:
        if now - state.last_triggered < config.cooldown_seconds:
            return False

    state.last_triggered = now
    state.trigger_count += 1
    callback(state)
    return True


def create_watchdog(
    callback: Callable[[WatchdogState], None],
    config: Optional[WatchdogConfig] = None,
) -> tuple[WatchdogState, Callable[[DiffScore], bool]]:
    """Factory that returns (state, observe_fn) for convenient use."""
    cfg = config or WatchdogConfig()
    state = WatchdogState()

    def observe(score: DiffScore) -> bool:
        return evaluate_watchdog(score, state, cfg, callback)

    return state, observe
