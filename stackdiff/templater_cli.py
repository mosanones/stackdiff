"""templater_cli.py — CLI entry-point for diff template rendering."""

from __future__ import annotations

import argparse
import json
import sys

from stackdiff.pipeline import run_pipeline
from stackdiff.diff_templater import list_templates, render_template


def build_templater_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="stackdiff-template",
        description="Render a diff result using a named output template.",
    )
    p.add_argument("base", help="Base config file (staging / old)")
    p.add_argument("compare", help="Compare config file (prod / new)")
    p.add_argument(
        "--template", "-t",
        default="compact",
        help="Template name (default: compact)",
    )
    p.add_argument(
        "--label-a", default="base", dest="label_a",
        help="Label for the base config",
    )
    p.add_argument(
        "--label-b", default="compare", dest="label_b",
        help="Label for the compare config",
    )
    p.add_argument(
        "--list", action="store_true",
        help="List available template names and exit",
    )
    p.add_argument(
        "--json", action="store_true", dest="as_json",
        help="Emit the TemplateResult as JSON",
    )
    return p


def main(argv: list[str] | None = None) -> int:  # noqa: UP006
    parser = build_templater_parser()
    args = parser.parse_args(argv)

    if args.list:
        for name in list_templates():
            print(name)
        return 0

    try:
        ctx = run_pipeline(args.base, args.compare)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 2

    try:
        result = render_template(
            ctx.diff,
            template_name=args.template,
            label_a=args.label_a,
            label_b=args.label_b,
        )
    except KeyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.as_json:
        print(json.dumps({"template": result.template_name, "rendered": result.rendered, "context": result.context}, indent=2))
    else:
        print(result.rendered)

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
