"""Named filter presets for common diff scenarios."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import json
from pathlib import Path

BUILTIN_PRESETS: Dict[str, dict] = {
    "secrets": {
        "description": "Show only sensitive/secret keys",
        "include": ["*password*", "*secret*", "*token*", "*key*", "*credential*"],
        "exclude": [],
    },
    "endpoints": {
        "description": "Show only URL and host configuration",
        "include": ["*url*", "*host*", "*endpoint*", "*port*", "*addr*"],
        "exclude": [],
    },
    "infra": {
        "description": "Exclude application-level keys, keep infra",
        "include": ["*"],
        "exclude": ["*log*", "*debug*", "*feature*"],
    },
    "safe": {
        "description": "Exclude secrets, show everything else",
        "include": ["*"],
        "exclude": ["*password*", "*secret*", "*token*", "*key*", "*credential*"],
    },
}


@dataclass
class FilterPreset:
    name: str
    description: str
    include: List[str] = field(default_factory=list)
    exclude: List[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "include": self.include,
            "exclude": self.exclude,
        }


def _preset_path(presets_dir: str) -> Path:
    return Path(presets_dir) / "presets.json"


def load_preset(name: str, presets_dir: Optional[str] = None) -> FilterPreset:
    if presets_dir:
        path = _preset_path(presets_dir)
        if path.exists():
            data = json.loads(path.read_text())
            if name in data:
                p = data[name]
                return FilterPreset(name=name, **p)
    if name in BUILTIN_PRESETS:
        p = BUILTIN_PRESETS[name]
        return FilterPreset(name=name, **p)
    raise KeyError(f"Preset '{name}' not found")


def list_presets(presets_dir: Optional[str] = None) -> List[FilterPreset]:
    presets = {k: FilterPreset(name=k, **v) for k, v in BUILTIN_PRESETS.items()}
    if presets_dir:
        path = _preset_path(presets_dir)
        if path.exists():
            data = json.loads(path.read_text())
            for name, p in data.items():
                presets[name] = FilterPreset(name=name, **p)
    return list(presets.values())


def save_preset(preset: FilterPreset, presets_dir: str) -> Path:
    path = _preset_path(presets_dir)
    Path(presets_dir).mkdir(parents=True, exist_ok=True)
    existing = json.loads(path.read_text()) if path.exists() else {}
    existing[preset.name] = {
        "description": preset.description,
        "include": preset.include,
        "exclude": preset.exclude,
    }
    path.write_text(json.dumps(existing, indent=2))
    return path
