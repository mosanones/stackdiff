"""CLI for managing diff archives."""
from __future__ import annotations

import argparse
import json
import sys

from stackdiff.diff_archiver import (
    DEFAULT_ARCHIVE_DIR,
    delete_archive,
    list_archives,
    load_archive,
)


def build_archiver_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stackdiff-archive",
        description="Manage stackdiff diff archives.",
    )
    parser.add_argument(
        "--archive-dir",
        default=DEFAULT_ARCHIVE_DIR,
        help="Directory where archives are stored.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    ls_p = sub.add_parser("list", help="List archive entries.")
    ls_p.add_argument("--label", default=None, help="Filter by label prefix.")
    ls_p.add_argument("--json", dest="as_json", action="store_true")

    show_p = sub.add_parser("show", help="Show a single archive entry.")
    show_p.add_argument("archive_id", help="Archive ID to display.")
    show_p.add_argument("--json", dest="as_json", action="store_true")

    del_p = sub.add_parser("delete", help="Delete an archive entry.")
    del_p.add_argument("archive_id", help="Archive ID to delete.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_archiver_parser()
    args = parser.parse_args(argv)

    if args.command == "list":
        ids = list_archives(archive_dir=args.archive_dir, label=args.label)
        if args.as_json:
            print(json.dumps(ids, indent=2))
        else:
            if not ids:
                print("No archives found.")
            for aid in ids:
                print(aid)
        return 0

    if args.command == "show":
        try:
            entry = load_archive(args.archive_id, archive_dir=args.archive_dir)
        except FileNotFoundError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        if args.as_json:
            print(json.dumps(entry.as_dict(), indent=2))
        else:
            print(f"ID:        {entry.archive_id}")
            print(f"Label:     {entry.label}")
            print(f"Timestamp: {entry.timestamp}")
            print(f"Report keys: {list(entry.report.keys())}")
        return 0

    if args.command == "delete":
        try:
            delete_archive(args.archive_id, archive_dir=args.archive_dir)
            print(f"Deleted archive: {args.archive_id}")
        except FileNotFoundError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        return 0

    return 0  # pragma: no cover


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
