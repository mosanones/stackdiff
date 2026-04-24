"""comparator_formatter.py — render ComparisonResult as text or JSON."""
from __future__ import annotations

import json

from stackdiff.diff_comparator import ComparisonResult


def format_comparison_text(result: ComparisonResult, label_prev: str = "previous", label_curr: str = "current") -> str:
    lines: list[str] = []
    lines.append(f"=== Diff Comparison: {label_prev} → {label_curr} ===")

    if result.new_keys:
        lines.append("\n[NEW differences]")
        for k in result.new_keys:
            lines.append(f"  + {k}")

    if result.resolved_keys:
        lines.append("\n[RESOLVED differences]")
        for k in result.resolved_keys:
            lines.append(f"  ✓ {k}")

    if result.changed_values:
        lines.append("\n[VALUE SHIFTS in persisting differences]")
        for k, v in result.changed_values.items():
            lines.append(f"  ~ {k}")
            lines.append(f"      before: {v['before']}")
            lines.append(f"      after:  {v['after']}")

    if result.persisting_keys:
        unchanged_persisting = [k for k in result.persisting_keys if k not in result.changed_values]
        if unchanged_persisting:
            lines.append("\n[PERSISTING (unchanged) differences]")
            for k in unchanged_persisting:
                lines.append(f"  = {k}")

    status_parts = []
    if result.is_regression:
        status_parts.append("REGRESSION")
    if result.is_improved:
        status_parts.append("IMPROVED")
    if not status_parts:
        status_parts.append("NO CHANGE")

    lines.append(f"\nStatus: {', '.join(status_parts)}")
    return "\n".join(lines)


def format_comparison_json(result: ComparisonResult) -> str:
    return json.dumps(result.as_dict(), indent=2)


def format_comparison_output(result: ComparisonResult, fmt: str = "text", **kwargs) -> str:
    if fmt == "json":
        return format_comparison_json(result)
    return format_comparison_text(result, **kwargs)
