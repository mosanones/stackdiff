"""CLI entry point for the diff-group sub-command."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from stackdiff.config_loader import load_config
from stackdiff.diff_engine import diff_configs
from stackdiff.diff_grouper import group_by_custom, group_by_namespace
from stackdiff.group_formatter import format_grouped_output


def build_group_parser(parent: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    desc = "Group diff keys by namespace or custom mapping."
    if parent is not None:
        parser = parent.add_parser("group", help=desc, description=desc)
    else:
        parser = argparse.ArgumentParser(prog="stackdiff-group", description=desc)

    parser.add_argument("file_a", help="First config file (staging)")
    parser.add_argument("file_b", help="Second config file (production)")
    parser.add_argument(
        "--format", choices=["text", "json"], default="text", dest="fmt"
    )
    parser.add_argument(
        "--label-a", default="a", help="Label for file_a"
    )
    parser.add_argument(
        "--label-b", default="b", help="Label for file_b"
    )
    parser.add_argument(
        "--mapping",
        metavar="JSON",
        default=None,
        help='Custom grouping as JSON object, e.g. \'{"db": ["database"]}\'',
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_group_parser()
    args = parser.parse_args(argv)

    try:
        cfg_a = load_config(args.file_a)
        cfg_b = load_config(args.file_b)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    diff = diff_configs(cfg_a, cfg_b)

    if args.mapping:
        try:
            mapping = json.loads(args.mapping)
        except json.JSONDecodeError as exc:
            print(f"Invalid --mapping JSON: {exc}", file=sys.stderr)
            return 2
        grouped = group_by_custom(diff, mapping)
    else:
        grouped = group_by_namespace(diff)

    output = format_grouped_output(grouped, fmt=args.fmt, label_a=args.label_a, label_b=args.label_b)
    print(output)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
