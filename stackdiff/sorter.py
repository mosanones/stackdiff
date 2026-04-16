"""Sorting utilities for diff output and config keys."""
from typing import Dict, Any, List, Optional
from stackdiff.diff_engine import DiffResult


SORT_KEY = "key"
SORT_STATUS = "status"
SORT_NONE = "none"

VALID_SORT_MODES = (SORT_KEY, SORT_STATUS, SORT_NONE)

STATUS_ORDER = {"removed": 0, "added": 1, "changed": 2, "unchanged": 3}


def sort_flat_config(cfg: Dict[str, Any], reverse: bool = False) -> Dict[str, Any]:
    """Return a new dict with keys sorted alphabetically."""
    return dict(sorted(cfg.items(), key=lambda item: item[0], reverse=reverse))


def sort_diff_result(result: DiffResult, mode: str = SORT_KEY, reverse: bool = False) -> DiffResult:
    """Return a new DiffResult with diffs sorted by *mode*.

    mode='key'    – alphabetical by key name (default)
    mode='status' – grouped by change status (removed, added, changed, unchanged)
    mode='none'   – original insertion order preserved
    """
    if mode not in VALID_SORT_MODES:
        raise ValueError(f"Invalid sort mode '{mode}'. Choose from {VALID_SORT_MODES}.")

    if mode == SORT_NONE:
        return result

    items: List[tuple] = list(result.diffs.items())

    if mode == SORT_KEY:
        items.sort(key=lambda kv: kv[0], reverse=reverse)
    elif mode == SORT_STATUS:
        items.sort(
            key=lambda kv: (STATUS_ORDER.get(kv[1].get("status", "unchanged"), 99), kv[0]),
            reverse=reverse,
        )

    sorted_diffs = dict(items)
    return DiffResult(
        diffs=sorted_diffs,
        label_a=result.label_a,
        label_b=result.label_b,
    )
