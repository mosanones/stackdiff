"""Compare two config dicts and produce a structured diff result."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DiffResult:
    added: dict[str, Any] = field(default_factory=dict)      # keys only in right
    removed: dict[str, Any] = field(default_factory=dict)    # keys only in left
    changed: dict[str, tuple[Any, Any]] = field(default_factory=dict)  # (left_val, right_val)
    unchanged: dict[str, Any] = field(default_factory=dict)

    @property
    def has_diff(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    def summary(self) -> str:
        parts = []
        if self.added:
            parts.append(f"{len(self.added)} added")
        if self.removed:
            parts.append(f"{len(self.removed)} removed")
        if self.changed:
            parts.append(f"{len(self.changed)} changed")
        if not parts:
            return "No differences found."
        return "Diff: " + ", ".join(parts) + "."


def diff_configs(
    left: dict[str, Any],
    right: dict[str, Any],
    ignore_keys: list[str] | None = None,
) -> DiffResult:
    """Compare left (e.g. staging) vs right (e.g. production) configs."""
    ignore = set(ignore_keys or [])
    all_keys = (set(left) | set(right)) - ignore

    result = DiffResult()
    for key in sorted(all_keys):
        in_left = key in left
        in_right = key in right

        if in_left and not in_right:
            result.removed[key] = left[key]
        elif in_right and not in_left:
            result.added[key] = right[key]
        elif left[key] != right[key]:
            result.changed[key] = (left[key], right[key])
        else:
            result.unchanged[key] = left[key]

    return result
