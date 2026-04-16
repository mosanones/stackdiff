"""High-level handler that wires the watcher to the pipeline and reporter."""

from typing import Optional
from stackdiff.pipeline import run_pipeline
from stackdiff.reporter import generate_report
from stackdiff.watcher import watch_configs, ConfigWatcher


def _make_callback(
    fmt: str,
    output: Optional[str],
    include: Optional[list],
    exclude: Optional[list],
    mask: bool,
):
    def callback(path_a: str, path_b: str) -> None:
        print(f"[stackdiff] Change detected — re-running diff: {path_a} vs {path_b}")
        try:
            result = run_pipeline(
                path_a,
                path_b,
                include_patterns=include or [],
                exclude_patterns=exclude or [],
                mask_sensitive=mask,
            )
            generate_report(
                result,
                fmt=fmt,
                output_path=output,
                label_a=path_a,
                label_b=path_b,
            )
        except Exception as exc:  # noqa: BLE001
            print(f"[stackdiff] Error during diff: {exc}")

    return callback


def start_watch(
    path_a: str,
    path_b: str,
    fmt: str = "text",
    output: Optional[str] = None,
    include: Optional[list] = None,
    exclude: Optional[list] = None,
    mask: bool = True,
    interval: float = 1.0,
) -> ConfigWatcher:
    """Create, seed and return a started ConfigWatcher (blocking in caller's thread)."""
    callback = _make_callback(fmt, output, include, exclude, mask)
    watcher = watch_configs(path_a, path_b, callback, interval=interval)
    return watcher
