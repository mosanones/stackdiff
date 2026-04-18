# Alert Rules Engine

The `stackdiff.alerter` module evaluates a set of configurable rules against a
`DiffScore` and `DiffSummary` and returns a list of `Alert` objects.

## Usage

```python
from stackdiff.alerter import evaluate_rules, format_alerts, DEFAULT_RULES

alerts = evaluate_rules(score, summary)
print(format_alerts(alerts))
```

## Alert Rules

Each `AlertRule` can specify one or more conditions:

| Field            | Type    | Description                                      |
|------------------|---------|--------------------------------------------------|
| `name`           | str     | Identifier shown in alert output                 |
| `min_score`      | float   | Trigger if `DiffScore.score >= min_score`        |
| `require_critical` | bool  | Trigger if any critical keys changed             |
| `require_label`  | str     | Trigger if `DiffScore.label` matches this value  |

## Default Rules

- **high_score** — triggers when score ≥ 70
- **critical_keys_changed** — triggers when critical keys are present in the summary
- **breaking_label** — triggers when the score label is `"breaking"`

## Alert Severity

- `critical` — score ≥ 90 or critical key changed
- `warning` — score between 70–89 or label match
- `info` — informational only

## Output

```
ALERTS:
  [CRITICAL] critical_keys_changed: Critical keys changed: db.password
  [WARNING] high_score: Diff score 85.0 exceeds threshold 70.0
```

If no rules are triggered, `format_alerts` returns `"No alerts triggered."`
