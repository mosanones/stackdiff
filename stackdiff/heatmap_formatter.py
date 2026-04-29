"""Formatters for DiffHeatmap output."""
from __future__ import annotations

import json

from stackdiff.diff_heatmap import DiffHeatmap

_BAR_WIDTH = 20


def _bar(frequency: float) -> str:
    filled = round(frequency * _BAR_WIDTH)
    return "[" + "#" * filled + "-" * (_BAR_WIDTH - filled) + "]"


def format_heatmap_text(heatmap: DiffHeatmap) -> str:
    if not heatmap.entries:
        return "Heatmap: no changes recorded across any diff.\n"

    lines = [
        f"Heatmap — {heatmap.total_diffs} diff(s) analysed",
        "-" * 55,
    ]
    for entry in heatmap.hottest:
        bar = _bar(entry.frequency)
        lines.append(
            f"{entry.key:<30} {bar}  {entry.change_count}x ({entry.frequency:.0%})"
        )
    return "\n".join(lines) + "\n"


def format_heatmap_json(heatmap: DiffHeatmap) -> str:
    return json.dumps(heatmap.as_dict(), indent=2)


def format_heatmap_output(heatmap: DiffHeatmap, fmt: str = "text") -> str:
    if fmt == "json":
        return format_heatmap_json(heatmap)
    return format_heatmap_text(heatmap)
