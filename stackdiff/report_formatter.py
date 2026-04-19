"""Format a FullReport as text or JSON for display or export."""

import json
from stackdiff.diff_report_builder import FullReport


def format_full_text(report: FullReport, label_a: str = "a", label_b: str = "b") -> str:
    lines: list[str] = []
    s = report.stats
    lines.append(f"=== Diff Report: {label_a} vs {label_b} ===")
    lines.append(f"Total keys : {s.total_keys}")
    lines.append(f"Added      : {s.added}")
    lines.append(f"Removed    : {s.removed}")
    lines.append(f"Changed    : {s.changed}")
    lines.append(f"Unchanged  : {s.unchanged}")
    lines.append("")
    sc = report.score
    lines.append(f"Risk Score : {sc.score} ({sc.label})")
    lines.append("")
    su = report.summary
    lines.append(f"Critical keys : {', '.join(su.critical_keys) or 'none'}")
    lines.append(f"High keys     : {', '.join(su.high_keys) or 'none'}")
    lines.append("")
    if report.alerts:
        lines.append("ALERTS:")
        for alert in report.alerts:
            lines.append(f"  [{alert.rule}] {alert.message}")
    else:
        lines.append("No alerts.")
    return "\n".join(lines)


def format_full_json(report: FullReport) -> str:
    return json.dumps(report.as_dict(), indent=2)


def format_full_output(report: FullReport, fmt: str = "text", **kwargs) -> str:
    if fmt == "json":
        return format_full_json(report)
    return format_full_text(report, **kwargs)
