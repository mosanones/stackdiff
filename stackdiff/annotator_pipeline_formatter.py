"""Formatters for AnnotatorPipelineResult output."""
import json
from stackdiff.diff_annotator_pipeline import AnnotatorPipelineResult


def format_pipeline_text(result: AnnotatorPipelineResult) -> str:
    lines = []
    score = result.score
    summary = result.summary
    lines.append(f"=== Annotator Pipeline Report ===")
    lines.append(f"Risk Score : {score.score:.1f}  ({score.label})")
    lines.append(
        f"Changes    : {summary.total_changes} total  "
        f"({len(summary.critical_keys)} critical, {len(summary.high_keys)} high)"
    )
    if result.annotated.annotations:
        lines.append("")
        lines.append("Annotations:")
        for ann in result.annotated.annotations:
            removed = ann.removed if ann.removed is not None else "(none)"
            added = ann.added if ann.added is not None else "(none)"
            lines.append(
                f"  [{ann.severity.upper():8}] {ann.key}  "
                f"({ann.category})  {removed!r} -> {added!r}"
            )
    recs = result.recommendations.recommendations
    if recs:
        lines.append("")
        lines.append("Recommendations:")
        for rec in recs:
            lines.append(f"  [{rec.priority.upper()}] {rec.key}: {rec.message}")
    return "\n".join(lines)


def format_pipeline_json(result: AnnotatorPipelineResult) -> str:
    return json.dumps(result.as_dict(), indent=2)


def format_pipeline_output(result: AnnotatorPipelineResult, fmt: str = "text") -> str:
    if fmt == "json":
        return format_pipeline_json(result)
    return format_pipeline_text(result)
