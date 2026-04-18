"""Append-only audit log for diff operations."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional


DEFAULT_LOG_DIR = Path.home() / ".stackdiff" / "audit"


@dataclass
class AuditEntry:
    timestamp: str
    operation: str
    source_a: str
    source_b: str
    score_label: Optional[str] = None
    total_changes: int = 0
    critical_count: int = 0
    tags: List[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "operation": self.operation,
            "source_a": self.source_a,
            "source_b": self.source_b,
            "score_label": self.score_label,
            "total_changes": self.total_changes,
            "critical_count": self.critical_count,
            "tags": self.tags,
        }


def _log_path(log_dir: Path) -> Path:
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / "audit.jsonl"


def record_entry(entry: AuditEntry, log_dir: Path = DEFAULT_LOG_DIR) -> Path:
    """Append an audit entry to the JSONL log file."""
    path = _log_path(log_dir)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry.as_dict()) + "\n")
    return path


def load_entries(log_dir: Path = DEFAULT_LOG_DIR) -> List[AuditEntry]:
    """Load all audit entries from the log file."""
    path = _log_path(log_dir)
    if not path.exists():
        return []
    entries = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                data = json.loads(line)
                entries.append(AuditEntry(**data))
    return entries


def make_entry(
    operation: str,
    source_a: str,
    source_b: str,
    score_label: Optional[str] = None,
    total_changes: int = 0,
    critical_count: int = 0,
    tags: Optional[List[str]] = None,
) -> AuditEntry:
    """Construct an AuditEntry with the current UTC timestamp."""
    return AuditEntry(
        timestamp=datetime.now(timezone.utc).isoformat(),
        operation=operation,
        source_a=source_a,
        source_b=source_b,
        score_label=score_label,
        total_changes=total_changes,
        critical_count=critical_count,
        tags=tags or [],
    )
