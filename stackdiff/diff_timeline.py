"""Build a chronological timeline of diff history entries."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from stackdiff.diff_history import load_history


@dataclass
class TimelineEvent:
    timestamp: str
    label: str
    total_changes: int
    added: int
    removed: int
    changed: int
    score: float | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "label": self.label,
            "total_changes": self.total_changes,
            "added": self.added,
            "removed": self.removed,
            "changed": self.changed,
            "score": self.score,
        }


@dataclass
class DiffTimeline:
    events: list[TimelineEvent] = field(default_factory=list)
    history_id: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "history_id": self.history_id,
            "event_count": len(self.events),
            "events": [e.as_dict() for e in self.events],
        }

    @property
    def latest(self) -> TimelineEvent | None:
        return self.events[-1] if self.events else None

    @property
    def peak_changes(self) -> TimelineEvent | None:
        if not self.events:
            return None
        return max(self.events, key=lambda e: e.total_changes)


def _entry_to_event(entry: dict[str, Any]) -> TimelineEvent:
    stats = entry.get("stats", {})
    added = stats.get("added", 0)
    removed = stats.get("removed", 0)
    changed = stats.get("changed", 0)
    return TimelineEvent(
        timestamp=entry.get("timestamp", ""),
        label=entry.get("label", "unknown"),
        total_changes=added + removed + changed,
        added=added,
        removed=removed,
        changed=changed,
        score=entry.get("score"),
    )


def build_timeline(
    history_id: str,
    history_dir: str | None = None,
    limit: int | None = None,
) -> DiffTimeline:
    """Load history entries and return a chronological DiffTimeline."""
    entries = load_history(history_id, history_dir=history_dir)
    events = [_entry_to_event(e) for e in entries]
    events.sort(key=lambda e: e.timestamp)
    if limit is not None:
        events = events[-limit:]
    return DiffTimeline(events=events, history_id=history_id)
