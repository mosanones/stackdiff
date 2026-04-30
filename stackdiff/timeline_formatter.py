"""Format DiffTimeline for text and JSON output."""
from __future__ import annotations

import json

from stackdiff.diff_timeline import DiffTimeline


def format_timeline_text(timeline: DiffTimeline) -> str:
    lines: list[str] = []
    lines.append(f"Timeline: {timeline.history_id}")
    lines.append(f"{'─' * 50}")
    if not timeline.events:
        lines.append("  (no events recorded)")
        return "\n".join(lines)
    for event in timeline.events:
        score_str = f"  score={event.score:.1f}" if event.score is not None else ""
        lines.append(
            f"  [{event.timestamp}] {event.label}"
            f"  +{event.added} -{event.removed} ~{event.changed}"
            f"  total={event.total_changes}{score_str}"
        )
    lines.append(f"{'─' * 50}")
    peak = timeline.peak_changes
    if peak:
        lines.append(f"Peak change event: {peak.timestamp} ({peak.total_changes} changes)")
    return "\n".join(lines)


def format_timeline_json(timeline: DiffTimeline) -> str:
    return json.dumps(timeline.as_dict(), indent=2)


def format_timeline_output(timeline: DiffTimeline, fmt: str = "text") -> str:
    if fmt == "json":
        return format_timeline_json(timeline)
    return format_timeline_text(timeline)
