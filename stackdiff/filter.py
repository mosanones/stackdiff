"""Key filtering utilities for stackdiff."""

from __future__ import annotations

import fnmatch
from typing import Iterable


def _matches_any(key: str, patterns: Iterable[str]) -> bool:
    """Return True if *key* matches at least one glob pattern."""
    return any(fnmatch.fnmatch(key, p) for p in patterns)


def filter_keys(
    flat: dict[str, str],
    include: list[str] | None = None,
    exclude: list[str] | None = None,
) -> dict[str, str]:
    """Return a filtered copy of *flat* config dict.

    Parameters
    ----------
    flat:
        Flattened config produced by ``config_loader._flatten``.
    include:
        Glob patterns; when provided only matching keys are kept.
    exclude:
        Glob patterns; matching keys are removed after include filtering.
    """
    result = dict(flat)

    if include:
        result = {k: v for k, v in result.items() if _matches_any(k, include)}

    if exclude:
        result = {k: v for k, v in result.items() if not _matches_any(k, exclude)}

    return result


def apply_filters(
    cfg_a: dict[str, str],
    cfg_b: dict[str, str],
    include: list[str] | None = None,
    exclude: list[str] | None = None,
) -> tuple[dict[str, str], dict[str, str]]:
    """Apply the same include/exclude filters to both configs."""
    return (
        filter_keys(cfg_a, include=include, exclude=exclude),
        filter_keys(cfg_b, include=include, exclude=exclude),
    )
