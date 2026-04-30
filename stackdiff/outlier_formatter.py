"""Formatters for DiffOutliers output."""
from __future__ import annotations

import json

from stackdiff.diff_outlier import DiffOutliers


def format_outlier_text(result: DiffOutliers) -> str:
    lines = [
        f"Outlier Detection  (threshold={result.threshold}, diffs={result.total_diffs})",
        "=" * 60,
    ]
    if not result.outliers:
        lines.append("No outlier keys detected.")
        return "\n".join(lines)

    for entry in result.outliers:
        pct = f"{entry.frequency * 100:.1f}%"
        lines.append(f"  {entry.key}  [{entry.change_count}/{entry.total_diffs} diffs, {pct}]")
        if entry.sample_removed is not None:
            lines.append(f"    - removed: {entry.sample_removed}")
        if entry.sample_added is not None:
            lines.append(f"    + added:   {entry.sample_added}")

    return "\n".join(lines)


def format_outlier_json(result: DiffOutliers) -> str:
    return json.dumps(result.as_dict(), indent=2)


def format_outlier_output(result: DiffOutliers, fmt: str = "text") -> str:
    if fmt == "json":
        return format_outlier_json(result)
    return format_outlier_text(result)
