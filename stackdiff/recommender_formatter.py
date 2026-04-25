"""Formats RecommendationReport for text and JSON output."""
import json
from stackdiff.diff_recommender import RecommendationReport

_PRIORITY_SYMBOLS = {"high": "!!", "medium": "! ", "low": "  "}


def format_recommendations_text(report: RecommendationReport) -> str:
    if not report.recommendations:
        return "No recommendations.\n"

    lines = ["=== Recommendations ==="]
    for rec in report.recommendations:
        sym = _PRIORITY_SYMBOLS.get(rec.priority, "  ")
        lines.append(f"[{sym}] [{rec.priority.upper()}] {rec.key}")
        lines.append(f"      {rec.message}")
        lines.append(f"      Action: {rec.action}")
    lines.append(f"\nTotal: {len(report.recommendations)} recommendation(s), "
                 f"{len(report.high_priority())} high-priority.")
    return "\n".join(lines) + "\n"


def format_recommendations_json(report: RecommendationReport) -> str:
    return json.dumps(report.as_dict(), indent=2)


def format_recommendations_output(report: RecommendationReport, fmt: str = "text") -> str:
    if fmt == "json":
        return format_recommendations_json(report)
    return format_recommendations_text(report)
