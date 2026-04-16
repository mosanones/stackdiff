"""Orchestrate the full stackdiff pipeline: load, filter, mask, diff, sort, validate."""

from pathlib import Path
from typing import Any

from stackdiff.config_loader import load_config
from stackdiff.filter import apply_filters
from stackdiff.masker import mask_config, mask_diff_values
from stackdiff.diff_engine import diff_configs, DiffResult
from stackdiff.sorter import sort_diff_result
from stackdiff.validator import validate, ValidationResult


def run_pipeline(
    base_path: str | Path,
    compare_path: str | Path,
    include_globs: list[str] | None = None,
    exclude_globs: list[str] | None = None,
    mask: bool = True,
    sensitive_patterns: list[str] | None = None,
    sort: str = "asc",
    required_keys: list[str] | None = None,
) -> tuple[DiffResult, ValidationResult]:
    """Load two configs, apply filters/masking, diff, sort, and validate."""
    base: dict[str, Any] = load_config(base_path)
    compare: dict[str, Any] = load_config(compare_path)

    base = apply_filters(base, include_globs=include_globs, exclude_globs=exclude_globs)
    compare = apply_filters(
        compare, include_globs=include_globs, exclude_globs=exclude_globs
    )

    validation = validate(base, compare, required_keys=required_keys)

    if mask:
        base = mask_config(base, sensitive_patterns)
        compare = mask_config(compare, sensitive_patterns)

    result: DiffResult = diff_configs(base, compare)

    if mask:
        result = mask_diff_values(result, sensitive_patterns)

    result = sort_diff_result(result, order=sort)

    return result, validation
