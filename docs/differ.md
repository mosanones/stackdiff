# Differ Module

The `stackdiff.differ` module provides high-level helpers that combine loading,
filtering, masking, and diffing into a single call.

## Functions

### `diff_files`

Compare two config files directly.

```python
from stackdiff.differ import diff_files

ctx = diff_files(
    "configs/staging.yaml",
    "configs/prod.yaml",
    left_label="staging",
    right_label="prod",
    include=["DB_*"],
    exclude=["DEBUG"],
    mask=True,
)

if ctx.result.has_diff():
    print(ctx.result.summary())
```

### `diff_against_snapshot`

Compare the current state of a config file against a previously saved snapshot.

```python
from stackdiff.differ import diff_against_snapshot

ctx = diff_against_snapshot(
    "configs/prod.yaml",
    tag="v1.4.2",
    label="current",
    snap_dir=".snapshots",
)

print("Baseline used:", ctx.baseline_used)
print("Snapshot tag:", ctx.snapshot_tag)
```

## DiffContext

| Field | Type | Description |
|---|---|---|
| `left_label` | str | Label for the left/baseline config |
| `right_label` | str | Label for the right/current config |
| `result` | DiffResult | The raw diff result |
| `baseline_used` | bool | True when compared against a snapshot |
| `snapshot_tag` | str \| None | Tag of the snapshot used as baseline |

## CLI Integration

The CLI `main` function delegates to `diff_files` for the standard two-file
comparison path and to `diff_against_snapshot` when `--snapshot` is supplied.
