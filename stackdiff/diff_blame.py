"""Blame module: attribute diff changes to likely sources (env, secret, infra, app)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from stackdiff.diff_engine import DiffResult

_SOURCE_PATTERNS: Dict[str, List[str]] = {
    "env": ["env", "environment", "stage", "region", "zone"],
    "secret": ["password", "secret", "token", "key", "cert", "credential"],
    "infra": ["host", "port", "endpoint", "url", "addr", "replica", "pool"],
    "app": ["debug", "log", "timeout", "retry", "feature", "flag", "version", "release"],
}


@dataclass
class BlameEntry:
    key: str
    change_type: str  # "removed", "added", "changed"
    old_value: Optional[str]
    new_value: Optional[str]
    source: str

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "change_type": self.change_type,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "source": self.source,
        }


@dataclass
class BlamedDiff:
    entries: List[BlameEntry] = field(default_factory=list)

    def by_source(self, source: str) -> List[BlameEntry]:
        return [e for e in self.entries if e.source == source]

    def sources_present(self) -> List[str]:
        seen = dict.fromkeys(e.source for e in self.entries)
        return list(seen)

    def as_dict(self) -> dict:
        return {"entries": [e.as_dict() for e in self.entries]}


def _infer_source(key: str) -> str:
    lower = key.lower()
    for source, patterns in _SOURCE_PATTERNS.items():
        if any(p in lower for p in patterns):
            return source
    return "unknown"


def blame_diff(result: DiffResult) -> BlamedDiff:
    """Assign a source category to every changed key in *result*."""
    entries: List[BlameEntry] = []

    for key, value in result.removed.items():
        entries.append(BlameEntry(key, "removed", str(value), None, _infer_source(key)))

    for key, value in result.added.items():
        entries.append(BlameEntry(key, "added", None, str(value), _infer_source(key)))

    for key, (old, new) in result.changed.items():
        entries.append(BlameEntry(key, "changed", str(old), str(new), _infer_source(key)))

    entries.sort(key=lambda e: (e.source, e.key))
    return BlamedDiff(entries=entries)
