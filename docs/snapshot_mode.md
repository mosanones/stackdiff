# Snapshot Mode

Stackdiff can persist a flattened config to disk as a **snapshot**, allowing you
to diff the current state of an environment against a previously captured baseline.

## Saving a snapshot

```bash
stackdiff snapshot save staging.yaml --label staging
```

This writes a JSON file to `.stackdiff_snapshots/staging.json` containing the
flat config, a UTC timestamp, and optional metadata.

## Comparing against a snapshot

```bash
stackdiff snapshot diff production.yaml --label staging
```

The current file is loaded and diffed against the stored snapshot using the
standard diff engine, so all existing flags (`--exit-diff`, `--format`, `--mask`,
`--include`, `--exclude`) apply.

## Listing snapshots

```bash
stackdiff snapshot list
```

## Deleting a snapshot

```bash
stackdiff snapshot delete staging
```

## Python API

```python
from stackdiff.snapshotter import save_snapshot, load_snapshot

cfg = {"db.host": "prod-db", "app.debug": "false"}
save_snapshot(cfg, label="production", metadata={"deployed_by": "ci"})

baseline = load_snapshot("production")
```

## Snapshot file format

```json
{
  "label": "production",
  "timestamp": 1718000000.0,
  "metadata": {"deployed_by": "ci"},
  "config": {
    "db.host": "prod-db",
    "app.debug": "false"
  }
}
```

Snapshots are stored in `.stackdiff_snapshots/` by default. Add this directory
to `.gitignore` or commit snapshots as baselines — your choice.
