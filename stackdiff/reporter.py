"""Generate diff reports in multiple formats and optionally write to file."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

from stackdiff.diff_engine import DiffResult
from stackdiff.formatter import format_output


def build_report(
    result: DiffResult,
    fmt: str = "text",
    label_a: str = "staging",
    label_b: str = "production",
) -> str:
    """Return a formatted report string for the given diff result."""
    return format_output(result, fmt=fmt, label_a=label_a, label_b=label_b)


def write_report(
    report: str,
    output_path: Optional[str] = None,
    fmt: str = "text",
) -> None:
    """Write *report* to *output_path* or stdout.

    When writing JSON to a file the content is pretty-printed; plain text is
    written as-is.
    """
    if output_path is None:
        sys.stdout.write(report)
        if not report.endswith("\n"):
            sys.stdout.write("\n")
        return

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if fmt == "json":
        # Re-serialise to ensure consistent indentation when saving to disk.
        try:
            data = json.loads(report)
            content = json.dumps(data, indent=2)
        except json.JSONDecodeError:
            content = report
    else:
        content = report

    path.write_text(content, encoding="utf-8")


def generate_report(
    result: DiffResult,
    fmt: str = "text",
    label_a: str = "staging",
    label_b: str = "production",
    output_path: Optional[str] = None,
) -> str:
    """Build and optionally persist a report; always returns the report string."""
    report = build_report(result, fmt=fmt, label_a=label_a, label_b=label_b)
    write_report(report, output_path=output_path, fmt=fmt)
    return report
