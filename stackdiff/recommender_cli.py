"""CLI entry point for the diff recommender."""
import argparse
import sys
from stackdiff.differ import diff_files
from stackdiff.annotator import annotate_diff
from stackdiff.scorer import score_annotated
from stackdiff.diff_stats import compute_stats
from stackdiff.diff_recommender import generate_recommendations
from stackdiff.recommender_formatter import format_recommendations_output


def build_recommender_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stackdiff-recommend",
        description="Generate actionable recommendations from a config diff.",
    )
    parser.add_argument("staging", help="Path to staging config file.")
    parser.add_argument("production", help="Path to production config file.")
    parser.add_argument(
        "--format", choices=["text", "json"], default="text", dest="fmt"
    )
    parser.add_argument(
        "--no-score", action="store_true", help="Skip score-based recommendations."
    )
    parser.add_argument(
        "--no-stats", action="store_true", help="Skip stats-based recommendations."
    )
    parser.add_argument(
        "--fail-on-high",
        action="store_true",
        help="Exit with code 1 if any high-priority recommendations exist.",
    )
    return parser


def main(argv=None) -> int:
    parser = build_recommender_parser()
    args = parser.parse_args(argv)

    ctx = diff_files(args.staging, args.production)
    annotated = annotate_diff(ctx.result)
    score = None if args.no_score else score_annotated(annotated)
    stats = None if args.no_stats else compute_stats(ctx.result)

    report = generate_recommendations(annotated, score=score, stats=stats)
    print(format_recommendations_output(report, fmt=args.fmt), end="")

    if args.fail_on_high and report.high_priority():
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
