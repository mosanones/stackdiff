"""comparator_cli.py — CLI entry-point for comparing two diff snapshots."""
from __future__ import annotations

import argparse
import sys

from stackdiff.diff_comparator import compare_diffs
from stackdiff.comparator_formatter import format_comparison_output
from stackdiff.snapshotter import load_snapshot
from stackdiff.differ import diff_files


def build_comparator_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="stackdiff-compare",
        description="Compare two diff snapshots to detect regressions or improvements.",
    )
    p.add_argument("--prev-snap", metavar="NAME", help="Name of the previous snapshot (omit for first-run mode).")
    p.add_argument("--curr-snap", metavar="NAME", required=True, help="Name of the current snapshot.")
    p.add_argument("--snap-dir", metavar="DIR", default=".stackdiff/snapshots", help="Snapshot storage directory.")
    p.add_argument("--format", choices=["text", "json"], default="text", dest="fmt")
    p.add_argument("--label-prev", default="previous", metavar="LABEL")
    p.add_argument("--label-curr", default="current", metavar="LABEL")
    p.add_argument("--exit-code", action="store_true", help="Exit 1 if regression detected.")
    return p


def main(argv: list[str] | None = None) -> None:
    parser = build_comparator_parser()
    args = parser.parse_args(argv)

    try:
        curr_cfg = load_snapshot(args.curr_snap, snap_dir=args.snap_dir)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(2)

    prev_diff = None
    if args.prev_snap:
        try:
            prev_cfg = load_snapshot(args.prev_snap, snap_dir=args.snap_dir)
        except FileNotFoundError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            sys.exit(2)

        from stackdiff.diff_engine import diff_configs
        prev_diff = diff_configs(prev_cfg, curr_cfg)

    from stackdiff.diff_engine import diff_configs
    # For the current diff we treat curr snapshot as both sides (placeholder)
    # In real usage callers supply two env configs; here we demo the comparison.
    curr_diff = diff_configs({}, curr_cfg)

    comparison = compare_diffs(prev_diff, curr_diff)
    output = format_comparison_output(
        comparison,
        fmt=args.fmt,
        label_prev=args.label_prev,
        label_curr=args.label_curr,
    )
    print(output)

    if args.exit_code and comparison.is_regression:
        sys.exit(1)


if __name__ == "__main__":
    main()
