"""Baseline management: save and compare configs against a named baseline."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

DEFAULT_BASELINE_DIR = Path(".stackdiff/baselines")


def _baseline_path(name: str, base_dir: Path = DEFAULT_BASELINE_DIR) -> Path:
    return base_dir / f"{name}.json"


def save_baseline(
    name: str,
    config: dict,
    base_dir: Path = DEFAULT_BASELINE_DIR,
) -> Path:
    """Persist a flat config dict as a named baseline."""
    base_dir.mkdir(parents=True, exist_ok=True)
    path = _baseline_path(name, base_dir)
    path.write_text(json.dumps(config, indent=2), encoding="utf-8")
    return path


def load_baseline(
    name: str,
    base_dir: Path = DEFAULT_BASELINE_DIR,
) -> dict:
    """Load a previously saved baseline. Raises FileNotFoundError if absent."""
    path = _baseline_path(name, base_dir)
    if not path.exists():
        raise FileNotFoundError(f"Baseline '{name}' not found at {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def list_baselines(base_dir: Path = DEFAULT_BASELINE_DIR) -> list[str]:
    """Return sorted list of available baseline names."""
    if not base_dir.exists():
        return []
    return sorted(p.stem for p in base_dir.glob("*.json"))


def delete_baseline(
    name: str,
    base_dir: Path = DEFAULT_BASELINE_DIR,
) -> bool:
    """Delete a baseline. Returns True if deleted, False if not found."""
    path = _baseline_path(name, base_dir)
    if path.exists():
        path.unlink()
        return True
    return False


def diff_against_baseline(
    name: str,
    current: dict,
    base_dir: Path = DEFAULT_BASELINE_DIR,
) -> dict:
    """Return a dict with keys: removed, added, changed vs the named baseline."""
    baseline = load_baseline(name, base_dir)
    removed = {k: v for k, v in baseline.items() if k not in current}
    added = {k: v for k, v in current.items() if k not in baseline}
    changed = {
        k: {"baseline": baseline[k], "current": current[k]}
        for k in baseline
        if k in current and baseline[k] != current[k]
    }
    return {"removed": removed, "added": added, "changed": changed}
