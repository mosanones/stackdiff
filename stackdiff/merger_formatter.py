"""Format a MergedDiff for human-readable or JSON output."""
import json
from typing import Optional

from stackdiff.diff_merger import MergedDiff

_RESET = "\033[0m"
_RED = "\033[31m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_BOLD = "\033[1m"


def _cell(entry: Optional[tuple]) -> str:
    if entry is None:
        return "(same)"
    old, new = entry
    if old is None:
        return f"{_GREEN}+{new}{_RESET}"
    if new is None:
        return f"{_RED}-{old}{_RESET}"
    return f"{_YELLOW}{old} → {new}{_RESET}"


def format_merged_text(merged: MergedDiff) -> str:
    lines = [f"{_BOLD}Merged Diff — {len(merged.labels)} environment(s){_RESET}"]
    header = "  ".join(f"[{lbl}]" for lbl in merged.labels)
    lines.append(f"  Key{' ' * 30}{header}")
    lines.append("-" * 72)
    for key in merged.all_keys():
        entries = merged.merged[key]
        cells = "   ".join(_cell(e) for e in entries)
        lines.append(f"  {key:<32}{cells}")
    if not merged.all_keys():
        lines.append("  (no differences found)")
    return "\n".join(lines)


def format_merged_json(merged: MergedDiff) -> str:
    out = {
        "labels": merged.labels,
        "keys": {},
    }
    for key in merged.all_keys():
        out["keys"][key] = [
            {"old": e[0], "new": e[1]} if e is not None else None
            for e in merged.merged[key]
        ]
    return json.dumps(out, indent=2)


def format_merged_output(merged: MergedDiff, fmt: str = "text") -> str:
    if fmt == "json":
        return format_merged_json(merged)
    return format_merged_text(merged)
