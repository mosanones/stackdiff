"""Cache diff results to avoid recomputing unchanged configs."""

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Optional

DEFAULT_CACHE_DIR = ".stackdiff_cache"


def _cache_path(key: str, cache_dir: str = DEFAULT_CACHE_DIR) -> Path:
    return Path(cache_dir) / f"{key}.json"


def _hash_configs(cfg_a: dict, cfg_b: dict) -> str:
    payload = json.dumps([cfg_a, cfg_b], sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()[:16]


def save_cache(cfg_a: dict, cfg_b: dict, result: dict, cache_dir: str = DEFAULT_CACHE_DIR) -> Path:
    """Serialize and save a diff result keyed by config hash."""
    os.makedirs(cache_dir, exist_ok=True)
    key = _hash_configs(cfg_a, cfg_b)
    path = _cache_path(key, cache_dir)
    entry = {"hash": key, "timestamp": time.time(), "result": result}
    path.write_text(json.dumps(entry, indent=2))
    return path


def load_cache(cfg_a: dict, cfg_b: dict, cache_dir: str = DEFAULT_CACHE_DIR, max_age: Optional[float] = None) -> Optional[dict]:
    """Return cached diff result if present and not expired, else None."""
    key = _hash_configs(cfg_a, cfg_b)
    path = _cache_path(key, cache_dir)
    if not path.exists():
        return None
    entry = json.loads(path.read_text())
    if max_age is not None:
        age = time.time() - entry.get("timestamp", 0)
        if age > max_age:
            return None
    return entry["result"]


def clear_cache(cache_dir: str = DEFAULT_CACHE_DIR) -> int:
    """Delete all cache files. Returns number of files removed."""
    cache = Path(cache_dir)
    if not cache.exists():
        return 0
    removed = 0
    for f in cache.glob("*.json"):
        f.unlink()
        removed += 1
    return removed


def list_cache_entries(cache_dir: str = DEFAULT_CACHE_DIR) -> list:
    """Return metadata for all cached entries."""
    cache = Path(cache_dir)
    if not cache.exists():
        return []
    entries = []
    for f in sorted(cache.glob("*.json")):
        try:
            data = json.loads(f.read_text())
            entries.append({"hash": data.get("hash"), "timestamp": data.get("timestamp"), "file": str(f)})
        except Exception:
            pass
    return entries
