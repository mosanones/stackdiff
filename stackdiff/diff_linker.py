"""diff_linker.py — link diff keys across multiple named environments."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from stackdiff.diff_engine import DiffResult


@dataclass
class LinkedKey:
    key: str
    environments: Dict[str, Optional[str]]  # env_name -> value (None if absent)

    def as_dict(self) -> dict:
        return {"key": self.key, "environments": self.environments}

    @property
    def is_consistent(self) -> bool:
        """True when all environments share the same non-None value."""
        values = [v for v in self.environments.values() if v is not None]
        return len(set(values)) <= 1 and len(values) == len(self.environments)

    @property
    def missing_in(self) -> List[str]:
        return [env for env, val in self.environments.items() if val is None]


@dataclass
class LinkedDiff:
    env_names: List[str]
    keys: List[LinkedKey] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "environments": self.env_names,
            "keys": [k.as_dict() for k in self.keys],
        }

    def inconsistent_keys(self) -> List[LinkedKey]:
        return [k for k in self.keys if not k.is_consistent]

    def keys_missing_in(self, env: str) -> List[LinkedKey]:
        return [k for k in self.keys if env in k.missing_in]


def link_diffs(named_configs: Dict[str, Dict[str, str]]) -> LinkedDiff:
    """Build a LinkedDiff from a mapping of env_name -> flat config dict."""
    env_names = list(named_configs.keys())
    all_keys: set = set()
    for cfg in named_configs.values():
        all_keys.update(cfg.keys())

    linked_keys: List[LinkedKey] = []
    for key in sorted(all_keys):
        envs = {env: named_configs[env].get(key) for env in env_names}
        linked_keys.append(LinkedKey(key=key, environments=envs))

    return LinkedDiff(env_names=env_names, keys=linked_keys)


def link_from_diff_results(named_results: Dict[str, DiffResult]) -> LinkedDiff:
    """Build a LinkedDiff from a mapping of env_name -> DiffResult.

    Each DiffResult contributes its combined left+right values so that
    all changed keys across environments are surfaced.
    """
    named_configs: Dict[str, Dict[str, str]] = {}
    for env, result in named_results.items():
        merged: Dict[str, str] = {}
        for k, v in (result.removed or {}).items():
            merged[k] = v
        for k, v in (result.added or {}).items():
            merged[k] = v
        for k, (old, _) in (result.changed or {}).items():
            merged[k] = old
        named_configs[env] = merged
    return link_diffs(named_configs)
