"""Format annotated diff results for display."""

import json
from typing import Optional
from stackdiff.annotator import AnnotatedDiff

SEVERITY_SYMBOLS = {
    "critical": "[!!]",
    "high": "[! ]",
    "medium": "[~ ]",
    "low": "[  ]",
}


def format_annotated_text(annotated: AnnotatedDiff, label_a: str = "a", label_b: str = "b") -> str:
    lines = [f"Annotated diff ({label_a} -> {label_b}):", ""]
    if not annotated.annotations:
        lines.append("  No differences found.")
        return "\n".join(lines)

    for ann in annotated.annotations:
        symbol = SEVERITY_SYMBOLS.get(ann.severity, "[  ]")
        category = f" [{ann.category}]" if ann.category else ""
        note = f" — {ann.note}" if ann.note else ""
        diff = annotated.diff
        if ann.key in diff.removed:
            change = f"removed (was: {diff.removed[ann.key]})"
        elif ann.key in diff.added:
            change = f"added (now: {diff.added[ann.key]})"
        else:
            old, new = diff.changed[ann.key]
            change = f"changed: {old} -> {new}"
        lines.append(f"  {symbol} {ann.key}{category}: {change}{note}")

    lines.append("")
    lines.append(f"  Total changes: {len(annotated.annotations)}")
    return "\n".join(lines)


def format_annotated_json(annotated: AnnotatedDiff) -> str:
    data = [
        {
            "key": a.key,
            "severity": a.severity,
            "category": a.category,
            "note": a.note,
        }
        for a in annotated.annotations
    ]
    return json.dumps({"annotations": data, "total": len(data)}, indent=2)


def format_annotated_output(annotated: AnnotatedDiff, fmt: str = "text",
                            label_a: str = "a", label_b: str = "b") -> str:
    if fmt == "json":
        return format_annotated_json(annotated)
    return format_annotated_text(annotated, label_a=label_a, label_b=label_b)
