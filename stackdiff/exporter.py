"""Export diff results to various file formats (CSV, Markdown)."""
from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import Optional

from stackdiff.diff_engine import DiffResult


def to_csv(result: DiffResult, label_a: str = "staging", label_b: str = "production") -> str:
    """Serialise a DiffResult to a CSV string."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["key", "status", label_a, label_b])

    for key, value in sorted(result.removed.items()):
        writer.writerow([key, "removed", value, ""])

    for key, value in sorted(result.added.items()):
        writer.writerow([key, "added", "", value])

    for key, (val_a, val_b) in sorted(result.changed.items()):
        writer.writerow([key, "changed", val_a, val_b])

    return output.getvalue()


def to_markdown(result: DiffResult, label_a: str = "staging", label_b: str = "production") -> str:
    """Serialise a DiffResult to a Markdown table string."""
    lines: list[str] = []
    lines.append(f"| key | status | {label_a} | {label_b} |")
    lines.append("|-----|--------|" + "-" * (len(label_a) + 2) + "|" + "-" * (len(label_b) + 2) + "|")

    for key, value in sorted(result.removed.items()):
        lines.append(f"| `{key}` | removed | `{value}` | |")

    for key, value in sorted(result.added.items()):
        lines.append(f"| `{key}` | added | | `{value}` |")

    for key, (val_a, val_b) in sorted(result.changed.items()):
        lines.append(f"| `{key}` | changed | `{val_a}` | `{val_b}` |")

    return "\n".join(lines) + "\n"


def export(result: DiffResult, fmt: str, path: Optional[str] = None,
           label_a: str = "staging", label_b: str = "production") -> str:
    """Export diff result to *fmt* ('csv' or 'markdown'), optionally writing to *path*."""
    if fmt == "csv":
        content = to_csv(result, label_a, label_b)
    elif fmt in ("markdown", "md"):
        content = to_markdown(result, label_a, label_b)
    else:
        raise ValueError(f"Unsupported export format: {fmt!r}")

    if path:
        Path(path).write_text(content, encoding="utf-8")

    return content
