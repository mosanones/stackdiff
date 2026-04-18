"""Track and compare diff scores over time using saved snapshots."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional
import json
from pathlib import Path

DEFAULT_TREND_DIR = Path(".stackdiff/trends")


@dataclass
class TrendEntry:
    timestamp: str
    label: str
    score: int
    total_changes: int
    critical: int
    high: int

    def as_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "label": self.label,
            "score": self.score,
            "total_changes": self.total_changes,
            "critical": self.critical,
            "high": self.high,
        }


@dataclass
class TrendReport:
    entries: List[TrendEntry] = field(default_factory=list)

    def latest(self) -> Optional[TrendEntry]:
        return self.entries[-1] if self.entries else None

    def as_dict(self) -> dict:
        return {"entries": [e.as_dict() for e in self.entries]}


def _trend_path(name: str, trend_dir: Path = DEFAULT_TREND_DIR) -> Path:
    trend_dir.mkdir(parents=True, exist_ok=True)
    return trend_dir / f"{name}.json"


def record_entry(name: str, entry: TrendEntry, trend_dir: Path = DEFAULT_TREND_DIR) -> None:
    path = _trend_path(name, trend_dir)
    entries = []
    if path.exists():
        entries = json.loads(path.read_text())
    entries.append(entry.as_dict())
    path.write_text(json.dumps(entries, indent=2))


def load_trend(name: str, trend_dir: Path = DEFAULT_TREND_DIR) -> TrendReport:
    path = _trend_path(name, trend_dir)
    if not path.exists():
        return TrendReport()
    raw = json.loads(path.read_text())
    entries = [TrendEntry(**e) for e in raw]
    return TrendReport(entries=entries)


def summarize_trend(report: TrendReport) -> dict:
    if not report.entries:
        return {"status": "no data"}
    scores = [e.score for e in report.entries]
    return {
        "count": len(scores),
        "min_score": min(scores),
        "max_score": max(scores),
        "avg_score": round(sum(scores) / len(scores), 2),
        "latest_label": report.latest().label,
    }
