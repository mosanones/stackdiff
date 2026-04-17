"""High-level diff comparison with snapshot baseline support."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from stackdiff.config_loader import load_config
from stackdiff.diff_engine import diff_configs, DiffResult
from stackdiff.snapshotter import load_snapshot, save_snapshot
from stackdiff.masker import mask_config
from stackdiff.filter import apply_filters


@dataclass
class DiffContext:
    left_label: str
    right_label: str
    result: DiffResult
    baseline_used: bool = False
    snapshot_tag: Optional[str] = None


def diff_files(
    left_path: str,
    right_path: str,
    left_label: str = "left",
    right_label: str = "right",
    include: list[str] | None = None,
    exclude: list[str] | None = None,
    mask: bool = True,
) -> DiffContext:
    """Load, filter, optionally mask, and diff two config files."""
    left = load_config(left_path)
    right = load_config(right_path)

    left = apply_filters(left, include=include, exclude=exclude)
    right = apply_filters(right, include=include, exclude=exclude)

    if mask:
        left = mask_config(left)
        right = mask_config(right)

    result = diff_configs(left, right, left_label=left_label, right_label=right_label)
    return DiffContext(left_label=left_label, right_label=right_label, result=result)


def diff_against_snapshot(
    current_path: str,
    tag: str,
    label: str = "current",
    snap_dir: str = ".snapshots",
    include: list[str] | None = None,
    exclude: list[str] | None = None,
    mask: bool = True,
) -> DiffContext:
    """Diff a live config file against a saved snapshot."""
    current = load_config(current_path)
    baseline = load_snapshot(tag, snap_dir=snap_dir)

    current = apply_filters(current, include=include, exclude=exclude)
    baseline = apply_filters(baseline, include=include, exclude=exclude)

    if mask:
        current = mask_config(current)
        baseline = mask_config(baseline)

    result = diff_configs(baseline, current, left_label=tag, right_label=label)
    return DiffContext(
        left_label=tag,
        right_label=label,
        result=result,
        baseline_used=True,
        snapshot_tag=tag,
    )
