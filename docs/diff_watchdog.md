# Diff Watchdog

The **watchdog** module monitors repeated diff runs and fires an alert callback
when a configurable risk threshold is breached too many times within a rolling
time window.

## Concepts

| Term | Description |
|------|-------------|
| **breach** | A single diff whose `DiffScore.score` ≥ `score_threshold` |
| **window** | Rolling time period (seconds) in which breaches are counted |
| **max_breaches** | Number of breaches required to trip the watchdog |
| **cooldown** | Minimum gap (seconds) between consecutive trigger events |

## Quick start

```python
from stackdiff.diff_watchdog import WatchdogConfig, create_watchdog
from stackdiff.scorer import score_diff

def on_alert(state):
    print(f"Watchdog tripped! Total triggers: {state.trigger_count}")

cfg = WatchdogConfig(
    score_threshold=40.0,
    window_seconds=300.0,
    max_breaches=3,
    cooldown_seconds=60.0,
)

state, observe = create_watchdog(on_alert, config=cfg)

# Call observe() after every scheduled diff run
score = score_diff(diff_result)
observe(score)
```

## API

### `WatchdogConfig`

```python
@dataclass
class WatchdogConfig:
    score_threshold: float = 40.0
    window_seconds: float  = 300.0
    max_breaches: int      = 3
    cooldown_seconds: float = 60.0
```

### `WatchdogState`

```python
@dataclass
class WatchdogState:
    breach_times: list[float]  # timestamps of breaches within the current window
    trigger_count: int         # total number of times the watchdog has fired
    last_trigger_time: float | None  # timestamp of the most recent trigger, or None
```

### `create_watchdog(callback, config=None)`

Factory function. Returns `(WatchdogState, observe_fn)` where `observe_fn`
accepts a `DiffScore` and returns `True` when the watchdog was tripped.

### `evaluate_watchdog(score, state, config, callback)`

Low-level function used by `observe_fn`. Useful when you manage state
externally (e.g. persisted between process restarts).

## Integration with the scheduler

Pass `observe` as the post-diff hook inside `schedule_handler.py`:

```python
state, observe = create_watchdog(on_alert)

def job():
    ctx = diff_files(file_a, file_b, options)
    observe(score_diff(ctx.result))

start_scheduled_diff(file_a, file_b, interval=60, on_result=job)
```
