"""linker_formatter.py — text and JSON formatters for LinkedDiff."""
from __future__ import annotations

import json
from typing import Literal

from stackdiff.diff_linker import LinkedDiff

_ABSENT = "<absent>"


def format_linked_text(linked: LinkedDiff) -> str:
    lines: list[str] = []
    envs = linked.env_names
    header_cols = ["KEY"] + envs
    col_width = max(30, *(len(e) + 4 for e in envs))

    header = "  ".join(c.ljust(col_width) for c in header_cols)
    lines.append(header)
    lines.append("-" * len(header))

    if not linked.keys:
        lines.append("(no keys)")
        return "\n".join(lines)

    for lk in linked.keys:
        marker = "!" if not lk.is_consistent else " "
        row_vals = [lk.key] + [
            str(lk.environments.get(env) if lk.environments.get(env) is not None else _ABSENT)
            for env in envs
        ]
        row = f"{marker} " + "  ".join(v.ljust(col_width - 2) for v in row_vals)
        lines.append(row)

    inconsistent = linked.inconsistent_keys()
    lines.append("")
    lines.append(f"Total keys: {len(linked.keys)}  |  Inconsistent: {len(inconsistent)}")
    return "\n".join(lines)


def format_linked_json(linked: LinkedDiff) -> str:
    data = linked.as_dict()
    data["summary"] = {
        "total_keys": len(linked.keys),
        "inconsistent_keys": len(linked.inconsistent_keys()),
    }
    return json.dumps(data, indent=2)


def format_linked_output(
    linked: LinkedDiff, fmt: Literal["text", "json"] = "text"
) -> str:
    if fmt == "json":
        return format_linked_json(linked)
    return format_linked_text(linked)
