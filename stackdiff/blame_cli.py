"""CLI entry-point for the blame sub-command."""
from __future__ import annotations

import argparse
import sys

from stackdiff.diff_blame import blame_diff
from stackdiff.blame_formatter import format_blamed_output
from stackdiff.pipeline import run_pipeline


def build_blame_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    description = "Show which source category (env/secret/infra/app) owns each change."
    if parent is not None:
        parser = parent.add_parser("blame", description=description, help=description)
    else:
        parser = argparse.ArgumentParser(prog="stackdiff-blame", description=description)

    parser.add_argument("file_a", help="Base config file (staging / old)")
    parser.add_argument("file_b", help="Target config file (production / new)")
    parser.add_argument("--label-a", default="a", metavar="LABEL", help="Label for file_a")
    parser.add_argument("--label-b", default="b", metavar="LABEL", help="Label for file_b")
    parser.add_argument(
        "--format", choices=["text", "json"], default="text", dest="fmt",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--filter-source",
        metavar="SOURCE",
        help="Only show entries for a specific source (env, secret, infra, app, unknown)",
    )
    parser.add_argument(
        "--fail-on-diff", action="store_true",
        help="Exit with code 1 when differences are found",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_blame_parser()
    args = parser.parse_args(argv)

    try:
        ctx = run_pipeline(args.file_a, args.file_b)
    except Exception as exc:  # pragma: no cover
        print(f"error: {exc}", file=sys.stderr)
        return 2

    blamed = blame_diff(ctx.result)

    if args.filter_source:
        from stackdiff.diff_blame import BlamedDiff
        filtered = BlamedDiff(entries=blamed.by_source(args.filter_source))
    else:
        filtered = blamed

    print(
        format_blamed_output(filtered, fmt=args.fmt, label_a=args.label_a, label_b=args.label_b),
        end="",
    )

    if args.fail_on_diff and filtered.entries:
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
