"""CLI sub-command for inspecting diff history."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from stackdiff.diff_history import clear_history, list_histories, load_history


def build_history_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # noqa: SLF001
    desc = "Inspect stored diff history."
    if parent is not None:
        p = parent.add_parser("history", help=desc)
    else:
        p = argparse.ArgumentParser(prog="stackdiff-history", description=desc)

    sub = p.add_subparsers(dest="history_cmd", required=True)

    ls = sub.add_parser("list", help="List all history names.")
    ls.add_argument("--dir", dest="history_dir", default=None)

    show = sub.add_parser("show", help="Show entries for a history name.")
    show.add_argument("name")
    show.add_argument("--last", type=int, default=None, metavar="N", help="Show last N entries.")
    show.add_argument("--dir", dest="history_dir", default=None)

    rm = sub.add_parser("clear", help="Delete a history.")
    rm.add_argument("name")
    rm.add_argument("--dir", dest="history_dir", default=None)

    return p


def _resolve_history_dir(args: argparse.Namespace) -> Path | None:
    """Return a Path for the history directory if specified, else None."""
    return Path(args.history_dir) if args.history_dir else None


def main(argv: list[str] | None = None) -> int:
    parser = build_history_parser()
    args = parser.parse_args(argv)
    hdir = _resolve_history_dir(args)

    if args.history_cmd == "list":
        names = list_histories(hdir)
        if not names:
            print("No histories found.")
        else:
            for n in names:
                print(n)
        return 0

    if args.history_cmd == "show":
        entries = load_history(args.name, hdir)
        if not entries:
            print(f"No history for '{args.name}'.")
            return 0
        if args.last:
            entries = entries[-args.last :]
        for e in entries:
            print(json.dumps(e, indent=2))
        return 0

    if args.history_cmd == "clear":
        deleted = clear_history(args.name, hdir)
        if deleted:
            print(f"History '{args.name}' cleared.")
        else:
            print(f"No history found for '{args.name}'.")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
