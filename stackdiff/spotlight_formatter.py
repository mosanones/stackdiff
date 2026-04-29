"""Formatters for DiffSpotlight output."""
from __future__ import annotations

import json

from stackdiff.diff_spotlight import DiffSpotlight

_SEVERITY_ICON = {
    "critical": "🔴",
    "high": "🟠",
    "medium": "🟡",
    "low": "🟢",
    "info": "⚪",
}


def format_spotlight_text(spotlight: DiffSpotlight) -> str:
    if not spotlight.entries:
        return "spotlight: no significant changes detected.\n"

    lines = [f"=== Diff Spotlight (score: {spotlight.total_score:.1f}) ==="]
    for i, entry in enumerate(spotlight.entries, start=1):
        icon = _SEVERITY_ICON.get(entry.severity, "?")
        lines.append(f"  {i}. {icon} [{entry.severity.upper()}] {entry.key}")
        lines.append(f"       reason : {entry.reason}")
        if entry.old_value is not None:
            lines.append(f"       before : {entry.old_value}")
        if entry.new_value is not None:
            lines.append(f"       after  : {entry.new_value}")
    return "\n".join(lines) + "\n"


def format_spotlight_json(spotlight: DiffSpotlight) -> str:
    return json.dumps(spotlight.as_dict(), indent=2)


def format_spotlight_output(spotlight: DiffSpotlight, fmt: str = "text") -> str:
    if fmt == "json":
        return format_spotlight_json(spotlight)
    return format_spotlight_text(spotlight)
