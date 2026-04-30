"""Formatters for DriftReport output."""
from __future__ import annotations

import json

from stackdiff.diff_drift import DriftReport


def format_drift_text(report: DriftReport) -> str:
    lines = ["=== Drift Report ==="]
    lines.append(f"Total runs analysed : {report.total_runs}")
    lines.append(f"Drifting keys       : {len(report.drifting_keys)}")
    lines.append(f"Stable changed keys : {len(report.stable_changed_keys)}")

    if not report.entries:
        lines.append("No changes detected across runs.")
        return "\n".join(lines)

    lines.append("")
    lines.append(f"{'KEY':<40} {'CHANGES':>7}  FIRST SEEN           LAST SEEN")
    lines.append("-" * 90)
    for entry in report.entries:
        drift_marker = " *" if entry.change_count > 1 else "  "
        lines.append(
            f"{entry.key:<40} {entry.change_count:>7}{drift_marker}  "
            f"{entry.first_seen:<20} {entry.last_seen}"
        )
        if entry.current_removed is not None:
            lines.append(f"  - removed : {entry.current_removed}")
        if entry.current_added is not None:
            lines.append(f"  + added   : {entry.current_added}")

    lines.append("")
    lines.append("(* = drifting key — changed in more than one run)")
    return "\n".join(lines)


def format_drift_json(report: DriftReport) -> str:
    return json.dumps(report.as_dict(), indent=2)


def format_drift_output(report: DriftReport, fmt: str = "text") -> str:
    if fmt == "json":
        return format_drift_json(report)
    return format_drift_text(report)
