"""CLI entry point for stackdiff."""

from __future__ import annotations

import argparse
import sys

from stackdiff.config_loader import load_config
from stackdiff.diff_engine import diff_configs
from stackdiff.filter import apply_filters
from stackdiff.reporter import generate_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stackdiff",
        description="Compare environment configs across deployments.",
    )
    parser.add_argument("file_a", help="First config file (e.g. staging)")
    parser.add_argument("file_b", help="Second config file (e.g. production)")
    parser.add_argument("--label-a", default="a", help="Label for file_a")
    parser.add_argument("--label-b", default="b", help="Label for file_b")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
        help="Output format",
    )
    parser.add_argument(
        "--exit-one-on-diff",
        action="store_true",
        help="Exit with code 1 when differences are found",
    )
    parser.add_argument(
        "--include",
        nargs="+",
        metavar="PATTERN",
        help="Glob patterns of keys to include",
    )
    parser.add_argument(
        "--exclude",
        nargs="+",
        metavar="PATTERN",
        help="Glob patterns of keys to exclude",
    )
    parser.add_argument("-o", "--output", help="Write report to this file")
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    cfg_a = load_config(args.file_a)
    cfg_b = load_config(args.file_b)

    cfg_a, cfg_b = apply_filters(cfg_a, cfg_b, include=args.include, exclude=args.exclude)

    result = diff_configs(cfg_a, cfg_b)

    generate_report(
        result,
        fmt=args.fmt,
        label_a=args.label_a,
        label_b=args.label_b,
        output_path=args.output,
    )

    if args.exit_one_on_diff and result.has_diff:
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
