"""Persist and retrieve a rolling history of diff results."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

DEFAULT_DIR = Path.home() / ".stackdiff" / "history"
MAX_ENTRIES = 100


def _history_path(history_dir: Path, name: str) -> Path:
    history_dir.mkdir(parents=True, exist_ok=True)
    return history_dir / f"{name}.jsonl"


def record_diff(name: str, result: dict, history_dir: Optional[Path] = None) -> Path:
    """Append a diff result entry to the named history file."""
    hdir = Path(history_dir) if history_dir else DEFAULT_DIR
    path = _history_path(hdir, name)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "result": result,
    }
    with path.open("a") as fh:
        fh.write(json.dumps(entry) + "\n")
    _trim(path)
    return path


def load_history(name: str, history_dir: Optional[Path] = None) -> List[dict]:
    """Return all history entries for *name*, oldest first."""
    hdir = Path(history_dir) if history_dir else DEFAULT_DIR
    path = _history_path(hdir, name)
    if not path.exists():
        return []
    entries = []
    with path.open() as fh:
        for line in fh:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def clear_history(name: str, history_dir: Optional[Path] = None) -> bool:
    """Delete the history file for *name*. Returns True if deleted."""
    hdir = Path(history_dir) if history_dir else DEFAULT_DIR
    path = _history_path(hdir, name)
    if path.exists():
        path.unlink()
        return True
    return False


def list_histories(history_dir: Optional[Path] = None) -> List[str]:
    """Return names of all stored histories."""
    hdir = Path(history_dir) if history_dir else DEFAULT_DIR
    if not hdir.exists():
        return []
    return [p.stem for p in sorted(hdir.glob("*.jsonl"))]


def _trim(path: Path) -> None:
    lines = path.read_text().splitlines(keepends=True)
    if len(lines) > MAX_ENTRIES:
        path.write_text("".join(lines[-MAX_ENTRIES:]))
