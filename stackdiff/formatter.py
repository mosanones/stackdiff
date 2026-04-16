"""Output formatters for diff results."""
from typing import Optional
from stackdiff.diff_engine import DiffResult

ANSI_RED = "\033[91m"
ANSI_GREEN = "\033[92m"
ANSI_YELLOW = "\033[93m"
ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"


def format_text(result: DiffResult, color: bool = True) -> str:
    """Format a DiffResult as a human-readable text diff."""
    lines = []

    if not result.has_diff():
        msg = "No differences found."
        return f"{ANSI_GREEN}{msg}{ANSI_RESET}" if color else msg

    lines.append(
        f"{ANSI_BOLD}Diff: {result.left_label} vs {result.right_label}{ANSI_RESET}"
        if color
        else f"Diff: {result.left_label} vs {result.right_label}"
    )
    lines.append("")

    for key in sorted(result.only_in_left):
        prefix = f"{ANSI_RED}- {key}: {result.left[key]}{ANSI_RESET}" if color else f"- {key}: {result.left[key]}"
        lines.append(prefix)

    for key in sorted(result.only_in_right):
        prefix = f"{ANSI_GREEN}+ {key}: {result.right[key]}{ANSI_RESET}" if color else f"+ {key}: {result.right[key]}"
        lines.append(prefix)

    for key in sorted(result.changed):
        if color:
            lines.append(f"{ANSI_YELLOW}~ {key}:{ANSI_RESET}")
            lines.append(f"  {ANSI_RED}- {result.left[key]}{ANSI_RESET}")
            lines.append(f"  {ANSI_GREEN}+ {result.right[key]}{ANSI_RESET}")
        else:
            lines.append(f"~ {key}:")
            lines.append(f"  - {result.left[key]}")
            lines.append(f"  + {result.right[key]}")

    lines.append("")
    lines.append(result.summary())
    return "\n".join(lines)


def format_json(result: DiffResult) -> str:
    """Format a DiffResult as JSON."""
    import json

    data = {
        "left_label": result.left_label,
        "right_label": result.right_label,
        "only_in_left": {k: result.left[k] for k in sorted(result.only_in_left)},
        "only_in_right": {k: result.right[k] for k in sorted(result.only_in_right)},
        "changed": {
            k: {"left": result.left[k], "right": result.right[k]}
            for k in sorted(result.changed)
        },
        "summary": result.summary(),
    }
    return json.dumps(data, indent=2)


def format_output(result: DiffResult, fmt: str = "text", color: bool = True) -> str:
    """Dispatch to the appropriate formatter."""
    if fmt == "json":
        return format_json(result)
    return format_text(result, color=color)
