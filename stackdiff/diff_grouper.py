"""Group diff results by key namespace or custom category."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from stackdiff.diff_engine import DiffResult


@dataclass
class KeyGroup:
    name: str
    keys: List[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {"name": self.name, "keys": self.keys}


@dataclass
class GroupedDiff:
    groups: Dict[str, KeyGroup] = field(default_factory=dict)
    ungrouped: List[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "groups": {k: v.as_dict() for k, v in self.groups.items()},
            "ungrouped": self.ungrouped,
        }


def _infer_namespace(key: str) -> Optional[str]:
    """Return the top-level namespace of a dotted key, or None."""
    parts = key.split(".")
    return parts[0] if len(parts) > 1 else None


def group_by_namespace(diff: DiffResult) -> GroupedDiff:
    """Group all changed keys by their top-level namespace prefix."""
    all_keys = list(
        set(diff.removed) | set(diff.added) | set(diff.changed)
    )
    groups: Dict[str, KeyGroup] = {}
    ungrouped: List[str] = []

    for key in sorted(all_keys):
        ns = _infer_namespace(key)
        if ns is None:
            ungrouped.append(key)
        else:
            if ns not in groups:
                groups[ns] = KeyGroup(name=ns)
            groups[ns].keys.append(key)

    return GroupedDiff(groups=groups, ungrouped=ungrouped)


def group_by_custom(diff: DiffResult, mapping: Dict[str, List[str]]) -> GroupedDiff:
    """Group keys according to a caller-supplied {group_name: [key_prefix, ...]} mapping."""
    all_keys = list(
        set(diff.removed) | set(diff.added) | set(diff.changed)
    )
    groups: Dict[str, KeyGroup] = {}
    assigned: set = set()

    for group_name, prefixes in mapping.items():
        grp = KeyGroup(name=group_name)
        for key in sorted(all_keys):
            if any(key == p or key.startswith(p + ".") for p in prefixes):
                grp.keys.append(key)
                assigned.add(key)
        if grp.keys:
            groups[group_name] = grp

    ungrouped = sorted(k for k in all_keys if k not in assigned)
    return GroupedDiff(groups=groups, ungrouped=ungrouped)
