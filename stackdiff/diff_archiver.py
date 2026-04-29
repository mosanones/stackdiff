"""Archive and retrieve full diff reports for long-term storage."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_ARCHIVE_DIR = ".stackdiff/archive"


@dataclass
class ArchiveEntry:
    archive_id: str
    label: str
    timestamp: str
    report: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "archive_id": self.archive_id,
            "label": self.label,
            "timestamp": self.timestamp,
            "report": self.report,
        }


def _archive_path(archive_dir: str | Path) -> Path:
    return Path(archive_dir)


def _entry_filename(archive_id: str) -> str:
    return f"{archive_id}.json"


def save_archive(
    report: dict[str, Any],
    label: str = "default",
    archive_dir: str | Path = DEFAULT_ARCHIVE_DIR,
) -> ArchiveEntry:
    """Persist a report dict as a timestamped archive entry."""
    ts = datetime.now(timezone.utc).isoformat()
    archive_id = f"{label}_{ts.replace(':', '-').replace('+', 'Z')}"
    path = _archive_path(archive_dir)
    path.mkdir(parents=True, exist_ok=True)
    entry = ArchiveEntry(archive_id=archive_id, label=label, timestamp=ts, report=report)
    (path / _entry_filename(archive_id)).write_text(
        json.dumps(entry.as_dict(), indent=2), encoding="utf-8"
    )
    return entry


def load_archive(
    archive_id: str, archive_dir: str | Path = DEFAULT_ARCHIVE_DIR
) -> ArchiveEntry:
    """Load a previously saved archive entry by its ID."""
    fpath = _archive_path(archive_dir) / _entry_filename(archive_id)
    if not fpath.exists():
        raise FileNotFoundError(f"Archive entry not found: {archive_id}")
    data = json.loads(fpath.read_text(encoding="utf-8"))
    return ArchiveEntry(**data)


def list_archives(
    archive_dir: str | Path = DEFAULT_ARCHIVE_DIR, label: str | None = None
) -> list[str]:
    """Return sorted archive IDs, optionally filtered by label prefix."""
    path = _archive_path(archive_dir)
    if not path.exists():
        return []
    ids = [f.stem for f in sorted(path.glob("*.json"))]
    if label:
        ids = [i for i in ids if i.startswith(label)]
    return ids


def delete_archive(
    archive_id: str, archive_dir: str | Path = DEFAULT_ARCHIVE_DIR
) -> None:
    """Remove an archive entry by ID."""
    fpath = _archive_path(archive_dir) / _entry_filename(archive_id)
    if not fpath.exists():
        raise FileNotFoundError(f"Archive entry not found: {archive_id}")
    fpath.unlink()
