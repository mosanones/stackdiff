"""CLI extensions for snapshot-based diffing via the differ module."""
from __future__ import annotations

import argparse
import sys

from stackdiff.differ import diff_files, diff_against_snapshot
from stackdiff.formatter import format_output
from stackdiff.reporter import generate_report


def build_differ_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="stackdiff-diff",
        description="Diff configs or compare against a snapshot baseline.",
    )
    p.add_argument("left", help="Left / staging config file")
    p.add_argument("right", nargs="?", help="Right / prod config file (omit to use snapshot)")
    p.add_argument("--left-label", default="left")
    p.add_argument("--right-label", default="right")
    p.add_argument("--snapshot", metavar="TAG", help="Compare right (or left) against this snapshot tag")
    p.add_argument("--snap-dir", default=".snapshots")
    p.add_argument("--include", nargs="*", metavar="PATTERN")
    p.add_argument("--exclude", nargs="*", metavar="PATTERN")
    p.add_argument("--no-mask", action="store_true")
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.add_argument("--output", metavar="FILE", help="Write report to file")
    p.add_argument("--fail-on-diff", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_differ_parser()
    args = parser.parse_args(argv)

    mask = not args.no_mask
    filters = dict(include=args.include, exclude=args.exclude)

    if args.snapshot:
        target = args.right or args.left
        ctx = diff_against_snapshot(
            target,
            tag=args.snapshot,
            label=args.right_label,
            snap_dir=args.snap_dir,
            mask=mask,
            **filters,
        )
    else:
        if not args.right:
            parser.error("right config file is required when --snapshot is not used")
        ctx = diff_files(
            args.left,
            args.right,
            left_label=args.left_label,
            right_label=args.right_label,
            mask=mask,
            **filters,
        )

    generate_report(
        ctx.result,
        fmt=args.format,
        output=args.output,
        left_label=ctx.left_label,
        right_label=ctx.right_label,
    )

    if args.fail_on_diff and ctx.result.has_diff():
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
