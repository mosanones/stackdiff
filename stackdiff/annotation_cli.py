"""CLI entry point for annotated diff output with severity and category tagging."""

import argparse
import sys

from stackdiff.differ import diff_files, diff_against_snapshot
from stackdiff.annotator import annotate
from stackdiff.annotation_formatter import format_annotated_output
from stackdiff.reporter import write_report


def build_annotation_parser() -> argparse.ArgumentParser:
    """Build argument parser for the annotation-aware diff CLI."""
    parser = argparse.ArgumentParser(
        prog="stackdiff-annotate",
        description="Compare configs and annotate differences by severity and category.",
    )

    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "--files",
        nargs=2,
        metavar=("FILE_A", "FILE_B"),
        help="Two config files to compare directly.",
    )
    source_group.add_argument(
        "--snapshot",
        nargs=2,
        metavar=("FILE", "SNAPSHOT_NAME"),
        help="Compare a config file against a saved snapshot.",
    )

    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--label-a",
        default="a",
        help="Label for the first config (default: a).",
    )
    parser.add_argument(
        "--label-b",
        default="b",
        help="Label for the second config (default: b).",
    )
    parser.add_argument(
        "--min-severity",
        choices=["low", "medium", "high", "critical"],
        default=None,
        help="Only show annotations at or above this severity level.",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        default=None,
        help="Write output to a file instead of stdout.",
    )
    parser.add_argument(
        "--exit-on-diff",
        action="store_true",
        help="Exit with code 1 if any differences are found.",
    )
    parser.add_argument(
        "--snapshot-dir",
        default=".stackdiff_snapshots",
        help="Directory where snapshots are stored (default: .stackdiff_snapshots).",
    )

    return parser


_SEVERITY_ORDER = ["low", "medium", "high", "critical"]


def main(argv=None) -> None:
    """Run the annotation CLI."""
    parser = build_annotation_parser()
    args = parser.parse_args(argv)

    # Obtain diff context
    if args.files:
        file_a, file_b = args.files
        context = diff_files(
            file_a,
            file_b,
            label_a=args.label_a,
            label_b=args.label_b,
        )
    else:
        config_file, snapshot_name = args.snapshot
        context = diff_against_snapshot(
            config_file,
            snapshot_name,
            label_a=args.label_a,
            label_b=args.label_b,
            snapshot_dir=args.snapshot_dir,
        )

    # Annotate the diff result
    annotated = annotate(context.diff_result)

    # Filter by minimum severity if requested
    if args.min_severity:
        min_idx = _SEVERITY_ORDER.index(args.min_severity)
        annotated = annotated.__class__(
            diff_result=annotated.diff_result,
            annotations=[
                a for a in annotated.annotations
                if _SEVERITY_ORDER.index(a.severity) >= min_idx
            ],
        )

    # Format output
    output_text = format_annotated_output(
        annotated,
        fmt=args.format,
        label_a=context.label_a,
        label_b=context.label_b,
    )

    # Write or print
    if args.output:
        write_report(output_text, args.output)
    else:
        print(output_text)

    if args.exit_on_diff and annotated.diff_result.has_diff:
        sys.exit(1)


if __name__ == "__main__":
    main()
