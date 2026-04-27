"""Format ClassifiedDiff results as text or JSON."""

from __future__ import annotations

import json

from stackdiff.diff_classifier import ClassifiedDiff

_CHANGE_SYMBOLS = {"added": "+", "removed": "-", "changed": "~"}


def format_classified_text(classified: ClassifiedDiff, label_a: str = "staging", label_b: str = "production") -> str:
    lines: list[str] = []
    if not classified.categories:
        lines.append("No differences found.")
        return "\n".join(lines)

    lines.append(f"Classified Diff  [{label_a}] vs [{label_b}]")
    lines.append("=" * 50)

    for category, keys in sorted(classified.categories.items()):
        lines.append(f"\n[{category.upper()}]")
        for ck in sorted(keys, key=lambda x: x.key):
            sym = _CHANGE_SYMBOLS.get(ck.change_type, "?")
            if ck.change_type == "removed":
                lines.append(f"  {sym} {ck.key}: {ck.staging_value!r} -> (missing)")
            elif ck.change_type == "added":
                lines.append(f"  {sym} {ck.key}: (missing) -> {ck.production_value!r}")
            else:
                lines.append(f"  {sym} {ck.key}: {ck.staging_value!r} -> {ck.production_value!r}")

    return "\n".join(lines)


def format_classified_json(classified: ClassifiedDiff) -> str:
    return json.dumps(classified.as_dict(), indent=2)


def format_classified_output(
    classified: ClassifiedDiff,
    fmt: str = "text",
    label_a: str = "staging",
    label_b: str = "production",
) -> str:
    if fmt == "json":
        return format_classified_json(classified)
    return format_classified_text(classified, label_a=label_a, label_b=label_b)
