"""Load and parse environment config files (YAML/JSON/dotenv)."""

import json
import os
from pathlib import Path
from typing import Any

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def load_config(path: str) -> dict[str, Any]:
    """Load a config file and return a flat key-value dict."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    suffix = p.suffix.lower()

    if suffix in (".yaml", ".yml"):
        return _load_yaml(p)
    elif suffix == ".json":
        return _load_json(p)
    elif suffix in (".env", "") or p.name.startswith(".env"):
        return _load_dotenv(p)
    else:
        raise ValueError(f"Unsupported config format: {suffix!r}")


def _load_yaml(p: Path) -> dict[str, Any]:
    if not HAS_YAML:
        raise RuntimeError("PyYAML is required to load YAML files: pip install pyyaml")
    with p.open() as f:
        data = yaml.safe_load(f) or {}
    return _flatten(data)


def _load_json(p: Path) -> dict[str, Any]:
    with p.open() as f:
        data = json.load(f)
    return _flatten(data)


def _load_dotenv(p: Path) -> dict[str, Any]:
    result: dict[str, Any] = {}
    with p.open() as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                result[key.strip()] = value.strip()
    return result


def _flatten(data: Any, prefix: str = "") -> dict[str, Any]:
    """Recursively flatten nested dicts using dot notation."""
    items: dict[str, Any] = {}
    if isinstance(data, dict):
        for k, v in data.items():
            full_key = f"{prefix}.{k}" if prefix else k
            items.update(_flatten(v, full_key))
    else:
        items[prefix] = data
    return items
