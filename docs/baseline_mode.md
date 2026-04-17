# Baseline Mode

Baseline mode lets you snapshot a config under a human-readable name and later
diff any config against it — useful for tracking intentional changes over time.

## Saving a baseline

```python
from stackdiff.baseline import save_baseline
from stackdiff.config_loader import load_config

cfg = load_config("configs/production.yaml")
save_baseline("prod-2024-06", cfg)
```

Baselines are stored as JSON files under `.stackdiff/baselines/` by default.

## Listing baselines

```python
from stackdiff.baseline import list_baselines

print(list_baselines())  # ['prod-2024-06', 'prod-2024-07']
```

## Diffing against a baseline

```python
from stackdiff.baseline import diff_against_baseline
from stackdiff.config_loader import load_config

current = load_config("configs/production.yaml")
result = diff_against_baseline("prod-2024-06", current)

print("Removed:", result["removed"])
print("Added:",   result["added"])
print("Changed:", result["changed"])
```

### Result structure

| Key | Description |
|---------|----------------------------------------------|
| `removed` | Keys present in baseline but not in current |
| `added` | Keys present in current but not in baseline |
| `changed` | Keys whose values differ, with both values |

## Deleting a baseline

```python
from stackdiff.baseline import delete_baseline

delete_baseline("prod-2024-06")
```

## Custom storage directory

All functions accept an optional `base_dir: Path` argument:

```python
save_baseline("staging", cfg, base_dir=Path("/var/stackdiff/baselines"))
```
