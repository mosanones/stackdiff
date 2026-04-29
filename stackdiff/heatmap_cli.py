"""CLI entry-point for the diff heatmap sub-command."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from stackdiff.diff_heatmap import build_heatmap
from stackdiff.diff_history import load_history
from stackdiff.heatmap_formatter import format_heatmap_output


def build_heatmap_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="stackdiff-heatmap",
        description="Show which config keys change most often across recorded history.",
    )
    p.add_argument(
        "--history-dir",
        default=".stackdiff/history",
        metavar="DIR",
        help="Directory that contains diff history files (default: .stackdiff/history).",
    )
    p.add_argument(
        "--label",
        metavar="LABEL",
        help="Restrict analysis to history entries with this label.",
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
        help="Output format (default: text).",
    )
    p.add_argument(
        "--top",
        type=int,
        default=0,
        metavar="N",
        help="Show only the top N hottest keys (0 = all).",
    )
    return p


def main(argv: list[str] | None = None) -> None:
    parser = build_heatmap_parser()
    args = parser.parse_args(argv)

    history_dir = Path(args.history_dir)
    entries = load_history(history_dir)

    if args.label:
        entries = [e for e in entries if e.get("label") == args.label]

    if not entries:
        print("No history entries found.", file=sys.stderr)
        sys.exit(0)

    # Reconstruct lightweight DiffResult-like objects from stored dicts
    from stackdiff.diff_engine import DiffResult

    diffs = [
        DiffResult(
            label_a=e.get("label_a", "a"),
            label_b=e.get("label_b", "b"),
            removed=e.get("removed", {}),
            added=e.get("added", {}),
            changed=e.get("changed", {}),
        )
        for e in entries
    ]

    heatmap = build_heatmap(diffs)

    if args.top > 0:
        heatmap.entries = heatmap.hottest[: args.top]

    print(format_heatmap_output(heatmap, fmt=args.fmt), end="")


if __name__ == "__main__":
    main()
