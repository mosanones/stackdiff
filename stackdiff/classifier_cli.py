"""CLI entry point for the diff classifier feature."""

from __future__ import annotations

import argparse
import sys

from stackdiff.config_loader import load_config
from stackdiff.diff_engine import diff_configs
from stackdiff.diff_classifier import classify_diff
from stackdiff.classifier_formatter import format_classified_output


def build_classifier_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stackdiff-classify",
        description="Classify config differences by category (auth, database, network, …)",
    )
    parser.add_argument("staging", help="Path to staging config file")
    parser.add_argument("production", help="Path to production config file")
    parser.add_argument(
        "--label-a", default="staging", metavar="LABEL", help="Label for first file"
    )
    parser.add_argument(
        "--label-b", default="production", metavar="LABEL", help="Label for second file"
    )
    parser.add_argument(
        "--format", choices=["text", "json"], default="text", dest="fmt",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--category", metavar="CAT",
        help="Show only keys belonging to this category",
    )
    parser.add_argument(
        "--exit-code", action="store_true",
        help="Exit with code 1 when differences are found",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_classifier_parser()
    args = parser.parse_args(argv)

    cfg_a = load_config(args.staging)
    cfg_b = load_config(args.production)
    result = diff_configs(cfg_a, cfg_b, label_a=args.label_a, label_b=args.label_b)
    classified = classify_diff(result)

    if args.category:
        from stackdiff.diff_classifier import ClassifiedDiff
        filtered = ClassifiedDiff(
            categories={
                k: v for k, v in classified.categories.items()
                if k == args.category
            }
        )
        classified = filtered

    output = format_classified_output(
        classified, fmt=args.fmt, label_a=args.label_a, label_b=args.label_b
    )
    print(output)

    if args.exit_code and classified.all_keys():
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
