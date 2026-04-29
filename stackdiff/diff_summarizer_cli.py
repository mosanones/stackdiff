"""CLI entry point for the diff summarizer — prints a human-readable or JSON
summary of changes including score, risk label, critical/high-priority keys,
and trend direction."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from stackdiff.pipeline import run_pipeline
from stackdiff.annotator import annotate
from stackdiff.scorer import score_annotated
from stackdiff.summarizer import build_summary


def build_summarizer_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stackdiff-summary",
        description="Summarise diff between two config files.",
    )
    parser.add_argument("left", help="Path to base config (e.g. staging)")
    parser.add_argument("right", help="Path to compare config (e.g. production)")
    parser.add_argument(
        "--label-left", default="left", metavar="LABEL", help="Label for left config"
    )
    parser.add_argument(
        "--label-right", default="right", metavar="LABEL", help="Label for right config"
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--fail-on-critical",
        action="store_true",
        help="Exit with code 2 if any critical keys are found",
    )
    return parser


def _format_text(summary) -> str:
    lines = [
        f"Summary: {summary.label} (score={summary.score:.1f})",
        f"  Total changes : {summary.total_changes}",
        f"  Critical keys : {summary.critical_count}",
        f"  High keys     : {summary.high_count}",
    ]
    if summary.critical_keys:
        lines.append("  Critical      : " + ", ".join(summary.critical_keys))
    if summary.high_keys:
        lines.append("  High          : " + ", ".join(summary.high_keys))
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> None:
    parser = build_summarizer_parser()
    args = parser.parse_args(argv)

    ctx = run_pipeline(
        left_path=Path(args.left),
        right_path=Path(args.right),
        label_left=args.label_left,
        label_right=args.label_right,
    )
    annotated = annotate(ctx.diff_result)
    score = score_annotated(annotated)
    summary = build_summary(score=score, annotated=annotated)

    if args.format == "json":
        print(json.dumps(summary.as_dict(), indent=2))
    else:
        print(_format_text(summary))

    if args.fail_on_critical and summary.critical_count > 0:
        sys.exit(2)


if __name__ == "__main__":  # pragma: no cover
    main()
