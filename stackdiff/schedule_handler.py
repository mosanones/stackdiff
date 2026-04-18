"""High-level handler that wires pipeline + reporter into a scheduler job."""

from typing import Optional
from stackdiff.scheduler import ScheduleConfig, ScheduleState, start_scheduler, stop_scheduler
from stackdiff.pipeline import run_pipeline
from stackdiff.reporter import generate_report


def _make_job(file_a: str, file_b: str, fmt: str, output: Optional[str], mask: bool) -> callable:
    def job() -> None:
        result = run_pipeline(file_a, file_b, mask_secrets=mask)
        generate_report(result["diff"], fmt=fmt, output=output,
                        label_a=file_a, label_b=file_b)
    return job


def start_scheduled_diff(
    file_a: str,
    file_b: str,
    interval: int,
    fmt: str = "text",
    output: Optional[str] = None,
    mask: bool = True,
    max_runs: Optional[int] = None,
    label: str = "scheduled-diff",
    on_error=None,
) -> ScheduleState:
    job = _make_job(file_a, file_b, fmt, output, mask)
    config = ScheduleConfig(
        interval_seconds=interval,
        label=label,
        max_runs=max_runs,
        on_error=on_error,
    )
    return start_scheduler(job, config)


def stop_scheduled_diff(state: ScheduleState) -> None:
    stop_scheduler(state)
