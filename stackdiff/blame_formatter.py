"""Formatters for BlamedDiff output."""
from __future__ import annotations

import json
from typing import Optional

from stackdiff.diff_blame import BlamedDiff

_CHANGE_SYMBOLS = {"removed": "-", "added": "+", "changed": "~"}


def format_blamed_text(blamed: BlamedDiff, label_a: str = "a", label_b: str = "b") -> str:
    if not blamed.entries:
        return "No differences found.\n"

    lines = [f"Blame report  ({label_a} → {label_b})\n" + "=" * 50]
    current_source: Optional[str] = None

    for entry in blamed.entries:
        if entry.source != current_source:
            current_source = entry.source
            lines.append(f"\n[{current_source.upper()}]")

        sym = _CHANGE_SYMBOLS.get(entry.change_type, "?")
        if entry.change_type == "removed":
            lines.append(f"  {sym} {entry.key}: {entry.old_value!r} (removed)")
        elif entry.change_type == "added":
            lines.append(f"  {sym} {entry.key}: {entry.new_value!r} (added)")
        else:
            lines.append(f"  {sym} {entry.key}: {entry.old_value!r} → {entry.new_value!r}")

    return "\n".join(lines) + "\n"


def format_blamed_json(blamed: BlamedDiff) -> str:
    return json.dumps(blamed.as_dict(), indent=2)


def format_blamed_output(
    blamed: BlamedDiff,
    fmt: str = "text",
    label_a: str = "a",
    label_b: str = "b",
) -> str:
    if fmt == "json":
        return format_blamed_json(blamed)
    return format_blamed_text(blamed, label_a=label_a, label_b=label_b)
