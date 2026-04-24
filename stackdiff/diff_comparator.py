"""diff_comparator.py — compare two DiffResults to identify regressions or improvements."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from stackdiff.diff_engine import DiffResult


@dataclass
class ComparisonResult:
    """Outcome of comparing a previous DiffResult against a current one."""
    new_keys: List[str] = field(default_factory=list)
    resolved_keys: List[str] = field(default_factory=list)
    persisting_keys: List[str] = field(default_factory=list)
    changed_values: Dict[str, dict] = field(default_factory=dict)

    @property
    def is_regression(self) -> bool:
        """True when new differences appeared that weren't present before."""
        return bool(self.new_keys or self.changed_values)

    @property
    def is_improved(self) -> bool:
        """True when previously differing keys are now resolved."""
        return bool(self.resolved_keys)

    def as_dict(self) -> dict:
        return {
            "new_keys": self.new_keys,
            "resolved_keys": self.resolved_keys,
            "persisting_keys": self.persisting_keys,
            "changed_values": self.changed_values,
            "is_regression": self.is_regression,
            "is_improved": self.is_improved,
        }


def _changed_keys(result: DiffResult) -> Dict[str, dict]:
    """Return a mapping of key -> {old, new} for every differing key."""
    out: Dict[str, dict] = {}
    for key in result.removed:
        out[key] = {"old": result.left.get(key), "new": None}
    for key in result.added:
        out[key] = {"old": None, "new": result.right.get(key)}
    for key in result.changed:
        out[key] = {"old": result.left.get(key), "new": result.right.get(key)}
    return out


def compare_diffs(
    previous: Optional[DiffResult],
    current: DiffResult,
) -> ComparisonResult:
    """Compare *previous* diff against *current* diff.

    Args:
        previous: The earlier DiffResult (may be None for first run).
        current:  The latest DiffResult.

    Returns:
        A :class:`ComparisonResult` describing what changed between the two diffs.
    """
    if previous is None:
        prev_keys: Dict[str, dict] = {}
    else:
        prev_keys = _changed_keys(previous)

    curr_keys = _changed_keys(current)

    new_keys = [k for k in curr_keys if k not in prev_keys]
    resolved_keys = [k for k in prev_keys if k not in curr_keys]
    persisting_keys = [k for k in curr_keys if k in prev_keys]

    changed_values: Dict[str, dict] = {}
    for k in persisting_keys:
        if curr_keys[k] != prev_keys[k]:
            changed_values[k] = {"before": prev_keys[k], "after": curr_keys[k]}

    return ComparisonResult(
        new_keys=sorted(new_keys),
        resolved_keys=sorted(resolved_keys),
        persisting_keys=sorted(persisting_keys),
        changed_values=changed_values,
    )
