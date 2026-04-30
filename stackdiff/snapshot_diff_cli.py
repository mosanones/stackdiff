"""CLI entry point for comparing two snapshots."""
from __future__ import annotations

import argparse
import json
import sys

from stackdiff.diff_snapshot_diff import compare_snapshots, list_comparable_snapshots
from stackdiff.annotation_formatter import format_annotated_output


def build_snapshot_diff_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stackdiff-snapshot-diff",
        description="Compare two saved snapshots and report differences.",
    )
    parser.add_argument("left", help="Name of the left (base) snapshot")
    parser.add_argument("right", help="Name of the right (compare) snapshot")
    parser.add_argument(
        "--snapshot-dir",
        default=None,
        metavar="DIR",
        help="Directory where snapshots are stored",
    )
    parser.add_argument(
        "--no-mask",
        action="store_true",
        default=False,
        help="Disable secret masking",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        default=False,
        help="List available snapshots and exit",
    )
    parser.add_argument(
        "--fail-on-diff",
        action="store_true",
        default=False,
        help="Exit with code 1 when differences are found",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_snapshot_diff_parser()
    # Make positional args optional so --list works alone
    parser.add_argument("_left", nargs="?", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    if args.list:
        names = list_comparable_snapshots(snapshot_dir=args.snapshot_dir)
        if names:
            print("\n".join(names))
        else:
            print("No snapshots found.")
        return

    comparison = compare_snapshots(
        left_name=args.left,
        right_name=args.right,
        snapshot_dir=args.snapshot_dir,
        mask_secrets=not args.no_mask,
    )

    if args.fmt == "json":
        print(json.dumps(comparison.as_dict(), indent=2))
    else:
        output = format_annotated_output(comparison.annotated, fmt="text")
        print(output)
        print(f"\nRisk score : {comparison.score.score} ({comparison.score.label})")
        print(f"Masked     : {comparison.masked}")

    if args.fail_on_diff and comparison.diff.has_diff():
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
