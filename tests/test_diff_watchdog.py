"""Tests for stackdiff.diff_watchdog."""
import pytest
from stackdiff.diff_watchdog import (
    WatchdogConfig,
    WatchdogState,
    create_watchdog,
    evaluate_watchdog,
    _prune_window,
)
from stackdiff.scorer import DiffScore


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _score(value: float) -> DiffScore:
    label = "critical" if value >= 70 else ("moderate" if value >= 40 else "clean")
    return DiffScore(score=value, label=label, breakdown={})


DEFAULT_CFG = WatchdogConfig(
    score_threshold=40.0,
    window_seconds=300.0,
    max_breaches=3,
    cooldown_seconds=60.0,
)


# ---------------------------------------------------------------------------
# _prune_window
# ---------------------------------------------------------------------------

def test_prune_removes_old_entries():
    state = WatchdogState()
    state.breaches.extend([100.0, 200.0, 500.0])
    _prune_window(state, window=300.0, now=600.0)
    assert list(state.breaches) == [500.0]


def test_prune_keeps_all_within_window():
    state = WatchdogState()
    state.breaches.extend([400.0, 450.0, 499.0])
    _prune_window(state, window=300.0, now=600.0)
    assert len(state.breaches) == 3


# ---------------------------------------------------------------------------
# evaluate_watchdog — no trigger
# ---------------------------------------------------------------------------

def test_low_score_does_not_breach():
    fired = []
    state = WatchdogState()
    result = evaluate_watchdog(_score(10.0), state, DEFAULT_CFG, fired.append, _now=1000.0)
    assert result is False
    assert len(state.breaches) == 0


def test_breach_below_max_does_not_trigger():
    fired = []
    state = WatchdogState()
    for t in [1000.0, 1010.0]:  # only 2 breaches, need 3
        evaluate_watchdog(_score(50.0), state, DEFAULT_CFG, fired.append, _now=t)
    assert fired == []


# ---------------------------------------------------------------------------
# evaluate_watchdog — trigger
# ---------------------------------------------------------------------------

def test_third_breach_triggers_callback():
    fired = []
    state = WatchdogState()
    for t in [1000.0, 1010.0, 1020.0]:
        evaluate_watchdog(_score(50.0), state, DEFAULT_CFG, fired.append, _now=t)
    assert len(fired) == 1
    assert state.trigger_count == 1


def test_cooldown_prevents_immediate_retrigger():
    fired = []
    state = WatchdogState()
    for t in [1000.0, 1010.0, 1020.0]:
        evaluate_watchdog(_score(50.0), state, DEFAULT_CFG, fired.append, _now=t)
    # 4th breach within cooldown window
    evaluate_watchdog(_score(50.0), state, DEFAULT_CFG, fired.append, _now=1030.0)
    assert len(fired) == 1  # still only one trigger


def test_trigger_fires_again_after_cooldown():
    fired = []
    state = WatchdogState()
    for t in [1000.0, 1010.0, 1020.0]:
        evaluate_watchdog(_score(50.0), state, DEFAULT_CFG, fired.append, _now=t)
    # After cooldown (60 s) add more breaches
    for t in [1090.0, 1100.0, 1110.0]:
        evaluate_watchdog(_score(50.0), state, DEFAULT_CFG, fired.append, _now=t)
    assert len(fired) == 2


def test_old_breaches_pruned_so_no_trigger():
    fired = []
    state = WatchdogState()
    # Two breaches long ago
    for t in [100.0, 110.0]:
        evaluate_watchdog(_score(50.0), state, DEFAULT_CFG, fired.append, _now=t)
    # One new breach — old ones fall outside window
    evaluate_watchdog(_score(50.0), state, DEFAULT_CFG, fired.append, _now=1000.0)
    assert fired == []


# ---------------------------------------------------------------------------
# create_watchdog factory
# ---------------------------------------------------------------------------

def test_create_watchdog_returns_state_and_callable():
    state, observe = create_watchdog(lambda s: None)
    assert isinstance(state, WatchdogState)
    assert callable(observe)


def test_create_watchdog_observe_triggers():
    fired = []
    cfg = WatchdogConfig(score_threshold=40.0, window_seconds=300.0, max_breaches=2, cooldown_seconds=0.0)
    state, observe = create_watchdog(fired.append, config=cfg)
    observe(_score(50.0))
    observe(_score(50.0))
    assert len(fired) == 1
