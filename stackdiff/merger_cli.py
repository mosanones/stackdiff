"""CLI entry-point for the diff-merger feature."""
import argparse
import sys
from typing import List

from stackdiff.diff_merger import merge_diffs
from stackdiff.merger_formatter import format_merged_output
from stackdiff.pipeline import run_pipeline


def build_merger_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="stackdiff-merge",
        description="Merge diffs from multiple environment pairs into one view.",
    )
    p.add_argument(
        "pairs",
        nargs="+",
        metavar="LABEL:FILE_A:FILE_B",
        help="One or more labelled config pairs in LABEL:fileA:fileB format.",
    )
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.add_argument(
        "--fail-on-diff",
        action="store_true",
        help="Exit 1 if any differences are found.",
    )
    p.add_argument("--mask-secrets", action="store_true", default=True)
    return p


def _parse_pairs(raw: List[str]):
    parsed = []
    for item in raw:
        parts = item.split(":", 2)
        if len(parts) != 3:
            print(f"ERROR: invalid pair spec '{item}' — expected LABEL:fileA:fileB", file=sys.stderr)
            sys.exit(2)
        parsed.append((parts[0], parts[1], parts[2]))
    return parsed


def main(argv=None):
    parser = build_merger_parser()
    args = parser.parse_args(argv)
    pairs = _parse_pairs(args.pairs)

    labelled_diffs = []
    for label, file_a, file_b in pairs:
        try:
            ctx = run_pipeline(file_a, file_b, mask_secrets=args.mask_secrets)
            labelled_diffs.append((label, ctx.diff))
        except Exception as exc:  # noqa: BLE001
            print(f"ERROR loading pair '{label}': {exc}", file=sys.stderr)
            sys.exit(2)

    merged = merge_diffs(labelled_diffs)
    print(format_merged_output(merged, fmt=args.format))

    if args.fail_on_diff and merged.all_keys():
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
