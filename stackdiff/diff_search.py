"""Search and query flat diff results by key pattern, value, or change type."""
from __future__ import annotations
from dataclasses import dataclass, field
from fnmatch import fnmatch
from typing import Optional
from stackdiff.diff_engine import DiffResult


@dataclass
class SearchQuery:
    key_pattern: Optional[str] = None
    value_contains: Optional[str] = None
    change_type: Optional[str] = None  # "added", "removed", "changed"


@dataclass
class SearchResult:
    matches: dict = field(default_factory=dict)

    def count(self) -> int:
        return len(self.matches)

    def as_dict(self) -> dict:
        return {"matches": self.matches, "count": self.count()}


def _change_type(key: str, result: DiffResult) -> Optional[str]:
    if key in result.added:
        return "added"
    if key in result.removed:
        return "removed"
    if key in result.changed:
        return "changed"
    return None


def _value_str(key: str, result: DiffResult) -> str:
    if key in result.added:
        return str(result.added[key])
    if key in result.removed:
        return str(result.removed[key])
    if key in result.changed:
        return str(result.changed[key])
    return ""


def search_diff(result: DiffResult, query: SearchQuery) -> SearchResult:
    all_keys = set(result.added) | set(result.removed) | set(result.changed)
    matches = {}
    for key in sorted(all_keys):
        if query.key_pattern and not fnmatch(key, query.key_pattern):
            continue
        ctype = _change_type(key, result)
        if query.change_type and ctype != query.change_type:
            continue
        val = _value_str(key, result)
        if query.value_contains and query.value_contains.lower() not in val.lower():
            continue
        matches[key] = {"change_type": ctype, "value": val}
    return SearchResult(matches=matches)
