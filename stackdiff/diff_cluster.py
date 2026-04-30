"""Cluster diff keys into similarity groups based on naming patterns and change types."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from stackdiff.diff_engine import DiffResult

_CLUSTER_PATTERNS: Dict[str, List[str]] = {
    "auth": ["password", "secret", "token", "key", "credential", "auth", "api_key"],
    "database": ["db_", "database", "postgres", "mysql", "mongo", "redis", "dsn"],
    "network": ["host", "port", "url", "endpoint", "addr", "socket", "proxy"],
    "logging": ["log", "debug", "trace", "verbose", "sentry", "datadog"],
    "feature_flags": ["flag", "feature", "enable", "disable", "toggle"],
    "infra": ["region", "zone", "cluster", "namespace", "replicas", "cpu", "memory"],
    "misc": [],
}


@dataclass
class ClusterEntry:
    key: str
    cluster: str
    old_value: Optional[str]
    new_value: Optional[str]
    change_type: str  # "added", "removed", "changed"

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "cluster": self.cluster,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "change_type": self.change_type,
        }


@dataclass
class DiffCluster:
    clusters: Dict[str, List[ClusterEntry]] = field(default_factory=dict)

    def keys_in_cluster(self, name: str) -> List[ClusterEntry]:
        return self.clusters.get(name, [])

    @property
    def cluster_names(self) -> List[str]:
        return [name for name, entries in self.clusters.items() if entries]

    def as_dict(self) -> dict:
        return {
            name: [e.as_dict() for e in entries]
            for name, entries in self.clusters.items()
            if entries
        }


def _infer_cluster(key: str) -> str:
    lower = key.lower()
    for cluster, patterns in _CLUSTER_PATTERNS.items():
        if cluster == "misc":
            continue
        if any(p in lower for p in patterns):
            return cluster
    return "misc"


def _change_type(old: Optional[str], new: Optional[str]) -> str:
    if old is None:
        return "added"
    if new is None:
        return "removed"
    return "changed"


def cluster_diff(result: DiffResult) -> DiffCluster:
    """Group all changed keys in *result* into named clusters."""
    clusters: Dict[str, List[ClusterEntry]] = {name: [] for name in _CLUSTER_PATTERNS}

    all_keys = set(result.removed) | set(result.added) | set(result.changed)
    for key in sorted(all_keys):
        old_val = result.removed.get(key) or (result.changed.get(key, (None, None))[0] if key in result.changed else None)
        new_val = result.added.get(key) or (result.changed.get(key, (None, None))[1] if key in result.changed else None)
        ctype = _change_type(
            result.removed.get(key, result.changed.get(key, [None])[0] if key in result.changed else None),
            result.added.get(key, result.changed.get(key, [None, None])[1] if key in result.changed else None),
        )
        cluster_name = _infer_cluster(key)
        entry = ClusterEntry(
            key=key,
            cluster=cluster_name,
            old_value=str(old_val) if old_val is not None else None,
            new_value=str(new_val) if new_val is not None else None,
            change_type=ctype,
        )
        clusters[cluster_name].append(entry)

    return DiffCluster(clusters=clusters)
