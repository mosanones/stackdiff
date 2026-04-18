"""CLI entry point for scheduled diff mode."""

import argparse
import sys
import time
from stackdiff.schedule_handler import start_scheduled_diff, stop_scheduled_diff


def build_schedule_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="stackdiff-schedule",
        description="Run diffs on a schedule between two config files.",
    )
    p.add_argument("file_a", help="First config file")
    p.add_argument("file_b", help="Second config file")
    p.add_argument("--interval", type=int, default=60, help="Seconds between runs (default: 60)")
    p.add_argument("--max-runs", type=int, default=None, help="Stop after N runs")
    p.add_argument("--format", choices=["text", "json"], default="text", dest="fmt")
    p.add_argument("--output", default=None, help="Write report to file")
    p.add_argument("--no-mask", action="store_true", help="Disable secret masking")
    p.add_argument("--label", default="scheduled-diff")
    return p


def main(argv=None) -> None:
    parser = build_schedule_parser()
    args = parser.parse_args(argv)

    def on_error(exc):
        print(f"[scheduler] error: {exc}", file=sys.stderr)

    state = start_scheduled_diff(
        file_a=args.file_a,
        file_b=args.file_b,
        interval=args.interval,
        fmt=args.fmt,
        output=args.output,
        mask=not args.no_mask,
        max_runs=args.max_runs,
        label=args.label,
        on_error=on_error,
    )
    print(f"[scheduler] started — interval={args.interval}s label={args.label}")
    try:
        while state.running:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[scheduler] stopping...")
        stop_scheduled_diff(state)
        print(f"[scheduler] done. runs={state.runs} errors={state.errors}")


if __name__ == "__main__":
    main()
