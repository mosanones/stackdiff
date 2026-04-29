"""linker_cli.py — CLI entry point for cross-environment key linking."""
from __future__ import annotations

import argparse
import sys
from typing import List

from stackdiff.config_loader import load_config
from stackdiff.diff_linker import link_diffs
from stackdiff.linker_formatter import format_linked_output


def build_linker_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stackdiff-link",
        description="Compare config keys across multiple named environments.",
    )
    parser.add_argument(
        "envs",
        nargs="+",
        metavar="NAME:FILE",
        help="One or more name:filepath pairs, e.g. staging:staging.yaml prod:prod.yaml",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--inconsistent-only",
        action="store_true",
        help="Only show keys that differ across environments",
    )
    return parser


def _parse_env_args(raw: List[str]) -> dict:
    named: dict = {}
    for item in raw:
        if ":" not in item:
            raise ValueError(f"Expected NAME:FILE, got: {item!r}")
        name, _, path = item.partition(":")
        named[name.strip()] = load_config(path.strip())
    return named


def main(argv: List[str] | None = None) -> int:
    parser = build_linker_parser()
    args = parser.parse_args(argv)

    try:
        named_configs = _parse_env_args(args.envs)
    except (ValueError, FileNotFoundError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    linked = link_diffs(named_configs)

    if args.inconsistent_only:
        from stackdiff.diff_linker import LinkedDiff
        linked = LinkedDiff(
            env_names=linked.env_names,
            keys=linked.inconsistent_keys(),
        )

    print(format_linked_output(linked, fmt=args.format))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
