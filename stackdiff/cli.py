"""CLI entry point for stackdiff."""
import argparse
import sys

from stackdiff.config_loader import load_config
from stackdiff.diff_engine import diff_configs
from stackdiff.formatter import format_output


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stackdiff",
        description="Compare environment configs across deployments.",
    )
    parser.add_argument("left", help="Path to the left/staging config file.")
    parser.add_argument("right", help="Path to the right/production config file.")
    parser.add_argument(
        "--left-label",
        default=None,
        help="Display label for the left config (default: filename).",
    )
    parser.add_argument(
        "--right-label",
        default=None,
        help="Display label for the right config (default: filename).",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI color output.",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        help="Exit with code 1 if differences are found.",
    )
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        left_cfg = load_config(args.left)
        right_cfg = load_config(args.right)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    left_label = args.left_label or args.left
    right_label = args.right_label or args.right

    result = diff_configs(left_cfg, right_cfg, left_label=left_label, right_label=right_label)
    output = format_output(result, fmt=args.format, color=not args.no_color)
    print(output)

    if args.exit_code and result.has_diff():
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
