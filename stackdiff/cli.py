"""Command-line interface for stackdiff."""
from __future__ import annotations

import argparse
import sys

from stackdiff.config_loader import load_config
from stackdiff.diff_engine import diff_configs
from stackdiff.reporter import generate_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stackdiff",
        description="Compare environment configs across deployments.",
    )
    parser.add_argument("file_a", help="Path to the first config file (e.g. staging).")
    parser.add_argument("file_b", help="Path to the second config file (e.g. production).")
    parser.add_argument(
        "--label-a", default="staging", help="Label for file_a (default: staging)."
    )
    parser.add_argument(
        "--label-b", default="production", help="Label for file_b (default: production)."
    )
    parser.add_argument(
        "--format",
        dest="fmt",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--output",
        dest="output_path",
        default=None,
        help="Write report to this file instead of stdout.",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit with code 1 when differences are found.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    config_a = load_config(args.file_a)
    config_b = load_config(args.file_b)

    result = diff_configs(config_a, config_b)

    generate_report(
        result,
        fmt=args.fmt,
        label_a=args.label_a,
        label_b=args.label_b,
        output_path=args.output_path,
    )

    if args.exit_code and (result.added or result.removed or result.changed):
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
