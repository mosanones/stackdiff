"""Snapshot configs to disk for later comparison."""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Dict, Any, Optional

DEFAULT_SNAPSHOT_DIR = ".stackdiff_snapshots"


def _snapshot_path(label: str, snapshot_dir: str) -> Path:
    safe = label.replace(os.sep, "_").replace(" ", "_")
    return Path(snapshot_dir) / f"{safe}.json"


def save_snapshot(
    config: Dict[str, Any],
    label: str,
    snapshot_dir: str = DEFAULT_SNAPSHOT_DIR,
    metadata: Optional[Dict[str, Any]] = None,
) -> Path:
    """Persist a flat config dict as a JSON snapshot."""
    Path(snapshot_dir).mkdir(parents=True, exist_ok=True)
    path = _snapshot_path(label, snapshot_dir)
    payload = {
        "label": label,
        "timestamp": time.time(),
        "metadata": metadata or {},
        "config": config,
    }
    path.write_text(json.dumps(payload, indent=2))
    return path


def load_snapshot(
    label: str,
    snapshot_dir: str = DEFAULT_SNAPSHOT_DIR,
) -> Dict[str, Any]:
    """Load a previously saved snapshot; returns the flat config dict."""
    path = _snapshot_path(label, snapshot_dir)
    if not path.exists():
        raise FileNotFoundError(f"No snapshot found for label '{label}' at {path}")
    payload = json.loads(path.read_text())
    return payload["config"]


def list_snapshots(snapshot_dir: str = DEFAULT_SNAPSHOT_DIR) -> list[str]:
    """Return labels of all saved snapshots."""
    d = Path(snapshot_dir)
    if not d.exists():
        return []
    return [p.stem for p in sorted(d.glob("*.json"))]


def delete_snapshot(
    label: str,
    snapshot_dir: str = DEFAULT_SNAPSHOT_DIR,
) -> bool:
    """Delete a snapshot; returns True if deleted, False if not found."""
    path = _snapshot_path(label, snapshot_dir)
    if path.exists():
        path.unlink()
        return True
    return False
