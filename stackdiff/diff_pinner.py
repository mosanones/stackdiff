"""diff_pinner.py — pin a diff result as an expected baseline to detect regressions."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from stackdiff.diff_engine import DiffResult

DEFAULT_PIN_DIR = ".stackdiff_pins"


@dataclass
class PinnedDiff:
    label: str
    removed: Dict[str, str]
    added: Dict[str, str]
    changed: Dict[str, List[str]]
    pinned_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def as_dict(self) -> dict:
        return {
            "label": self.label,
            "removed": self.removed,
            "added": self.added,
            "changed": self.changed,
            "pinned_at": self.pinned_at,
        }


def _pin_path(label: str, pin_dir: str = DEFAULT_PIN_DIR) -> Path:
    safe = label.replace(os.sep, "_").replace(" ", "_")
    return Path(pin_dir) / f"{safe}.json"


def pin_diff(result: DiffResult, label: str, pin_dir: str = DEFAULT_PIN_DIR) -> PinnedDiff:
    """Persist *result* as a named pin."""
    Path(pin_dir).mkdir(parents=True, exist_ok=True)
    pinned = PinnedDiff(
        label=label,
        removed=dict(result.removed),
        added=dict(result.added),
        changed={k: list(v) for k, v in result.changed.items()},
    )
    path = _pin_path(label, pin_dir)
    path.write_text(json.dumps(pinned.as_dict(), indent=2))
    return pinned


def load_pin(label: str, pin_dir: str = DEFAULT_PIN_DIR) -> PinnedDiff:
    """Load a previously saved pin by label."""
    path = _pin_path(label, pin_dir)
    if not path.exists():
        raise FileNotFoundError(f"No pin found for label '{label}' in {pin_dir}")
    data = json.loads(path.read_text())
    return PinnedDiff(
        label=data["label"],
        removed=data["removed"],
        added=data["added"],
        changed=data["changed"],
        pinned_at=data["pinned_at"],
    )


def list_pins(pin_dir: str = DEFAULT_PIN_DIR) -> List[str]:
    """Return labels of all saved pins."""
    base = Path(pin_dir)
    if not base.exists():
        return []
    return [p.stem for p in sorted(base.glob("*.json"))]


def delete_pin(label: str, pin_dir: str = DEFAULT_PIN_DIR) -> bool:
    """Delete a pin; returns True if it existed."""
    path = _pin_path(label, pin_dir)
    if path.exists():
        path.unlink()
        return True
    return False


def compare_to_pin(result: DiffResult, label: str, pin_dir: str = DEFAULT_PIN_DIR) -> dict:
    """Compare *result* against a saved pin and return a deviation report."""
    pin = load_pin(label, pin_dir)
    current_removed = set(result.removed)
    current_added = set(result.added)
    current_changed = set(result.changed)
    pinned_removed = set(pin.removed)
    pinned_added = set(pin.added)
    pinned_changed = set(pin.changed)
    return {
        "label": label,
        "new_removals": sorted(current_removed - pinned_removed),
        "resolved_removals": sorted(pinned_removed - current_removed),
        "new_additions": sorted(current_added - pinned_added),
        "resolved_additions": sorted(pinned_added - current_added),
        "new_changes": sorted(current_changed - pinned_changed),
        "resolved_changes": sorted(pinned_changed - current_changed),
        "is_deviation": bool(
            (current_removed - pinned_removed)
            or (current_added - pinned_added)
            or (current_changed - pinned_changed)
        ),
    }
