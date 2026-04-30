"""CLI entry point for the annotator pipeline command."""
import argparse
import sys

from stackdiff.pipeline import run_pipeline
from stackdiff.diff_annotator_pipeline import run_annotator_pipeline
from stackdiff.annotator_pipeline_formatter import format_pipeline_output


def build_annotator_pipeline_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stackdiff-annotate-pipeline",
        description="Run full annotation pipeline: annotate, score, summarise, recommend.",
    )
    parser.add_argument("base", help="Base config file (staging)")
    parser.add_argument("compare", help="Compare config file (production)")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--fail-on-critical",
        action="store_true",
        help="Exit with code 2 if any critical annotations are found",
    )
    parser.add_argument(
        "--label-base",
        default="base",
        help="Label for the base config (default: base)",
    )
    parser.add_argument(
        "--label-compare",
        default="compare",
        help="Label for the compare config (default: compare)",
    )
    return parser


def main(argv=None) -> int:
    parser = build_annotator_pipeline_parser()
    args = parser.parse_args(argv)

    ctx = run_pipeline(
        args.base,
        args.compare,
        label_a=args.label_base,
        label_b=args.label_compare,
    )
    result = run_annotator_pipeline(ctx.diff)
    output = format_pipeline_output(result, fmt=args.format)
    print(output)

    if args.fail_on_critical and result.summary.critical_keys:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
