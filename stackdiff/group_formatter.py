"""Format GroupedDiff results for text and JSON output."""
from __future__ import annotations

import json
from typing import Optional

from stackdiff.diff_grouper import GroupedDiff


def format_grouped_text(grouped: GroupedDiff, label_a: str = "a", label_b: str = "b") -> str:
    lines = [f"Grouped diff ({label_a} → {label_b})"]
    lines.append("=" * 40)

    if not grouped.groups and not grouped.ungrouped:
        lines.append("No changes detected.")
        return "\n".join(lines)

    for group_name, grp in sorted(grouped.groups.items()):
        lines.append(f"\n[{group_name}]")
        for key in grp.keys:
            lines.append(f"  • {key}")

    if grouped.ungrouped:
        lines.append("\n[ungrouped]")
        for key in grouped.ungrouped:
            lines.append(f"  • {key}")

    return "\n".join(lines)


def format_grouped_json(grouped: GroupedDiff, label_a: str = "a", label_b: str = "b") -> str:
    payload = {
        "labels": {"a": label_a, "b": label_b},
        "grouped_diff": grouped.as_dict(),
    }
    return json.dumps(payload, indent=2)


def format_grouped_output(
    grouped: GroupedDiff,
    fmt: str = "text",
    label_a: str = "a",
    label_b: str = "b",
) -> str:
    if fmt == "json":
        return format_grouped_json(grouped, label_a, label_b)
    return format_grouped_text(grouped, label_a, label_b)
