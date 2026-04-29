"""sanitizer_cli.py — CLI entry-point for the diff sanitizer."""
from __future__ import annotations

import argparse
import json
import sys

from stackdiff.config_loader import load_config
from stackdiff.diff_sanitizer import SanitizeOptions, sanitize_config


def build_sanitizer_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="stackdiff-sanitize",
        description="Sanitize a config file and report what was changed.",
    )
    p.add_argument("file", help="Path to the config file (YAML, JSON, or .env).")
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    p.add_argument(
        "--lowercase-keys",
        action="store_true",
        default=False,
        help="Normalise all keys to lowercase.",
    )
    p.add_argument(
        "--drop-nulls",
        action="store_true",
        default=False,
        help="Drop keys whose value is null/None.",
    )
    p.add_argument(
        "--no-redact-urls",
        action="store_true",
        default=False,
        help="Disable redaction of embedded URL credentials.",
    )
    p.add_argument(
        "--show-sanitized",
        action="store_true",
        default=False,
        help="Also print the sanitized config values.",
    )
    return p


def _format_text(result, show_sanitized: bool) -> str:
    lines = []
    if result.redacted_keys:
        lines.append("Redacted keys:")
        for k in result.redacted_keys:
            lines.append(f"  - {k}")
    if result.dropped_keys:
        lines.append("Dropped keys:")
        for k in result.dropped_keys:
            lines.append(f"  - {k}")
    if not result.was_modified():
        lines.append("No changes — config is already clean.")
    if show_sanitized:
        lines.append("\nSanitized config:")
        for k, v in result.sanitized.items():
            lines.append(f"  {k} = {v}")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = build_sanitizer_parser()
    args = parser.parse_args(argv)

    try:
        cfg = load_config(args.file)
    except Exception as exc:  # noqa: BLE001
        print(f"Error loading config: {exc}", file=sys.stderr)
        return 1

    opts = SanitizeOptions(
        lowercase_keys=args.lowercase_keys,
        drop_null_values=args.drop_nulls,
        redact_url_credentials=not args.no_redact_urls,
    )
    result = sanitize_config(cfg, opts)

    if args.format == "json":
        payload = result.as_dict()
        if args.show_sanitized:
            payload["sanitized"] = result.sanitized
        print(json.dumps(payload, indent=2))
    else:
        print(_format_text(result, args.show_sanitized))

    return 0


if __name__ == "__main__":
    sys.exit(main())
