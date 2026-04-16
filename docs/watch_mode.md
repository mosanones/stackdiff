# Watch Mode

`stackdiff` can continuously monitor two config files and re-run the diff
whenever either file changes on disk.

## CLI usage

```bash
# Watch staging vs production YAML, re-diff every 2 seconds
stackdiff watch staging.yaml production.yaml --interval 2

# Watch and write results to a file in JSON format
stackdiff watch staging.yaml production.yaml --format json --output diff.json

# Watch with key filtering and sensitive-value masking (on by default)
stackdiff watch staging.env production.env --exclude 'AWS_*' --mask
```

## Programmatic usage

```python
from stackdiff.watch_handler import start_watch

watcher = start_watch(
    "staging.yaml",
    "production.yaml",
    fmt="text",
    interval=1.0,
    mask=True,
)
watcher.start()  # blocks; Ctrl-C to exit
```

## How it works

1. `ConfigWatcher` polls `os.path.getmtime()` on both files every `interval` seconds.
2. When a modification time changes the registered callback is invoked with both paths.
3. The callback calls `run_pipeline` → `generate_report`, printing or writing the result.
4. If a file is temporarily missing (e.g. during an atomic write) the watcher skips
   that tick silently and retries on the next interval.

## Stopping the watcher

Call `watcher.stop()` from another thread, or send `SIGINT` (Ctrl-C) when running
from the CLI.
