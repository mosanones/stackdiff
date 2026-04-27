"""Classify diff results into named change categories for reporting and routing."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from stackdiff.diff_engine import DiffResult

# Ordered from most to least specific
_CATEGORY_PATTERNS: Dict[str, List[str]] = {
    "auth": ["password", "secret", "token", "api_key", "auth", "credential"],
    "database": ["db_", "database", "postgres", "mysql", "redis", "mongo"],
    "network": ["host", "port", "url", "endpoint", "address", "socket"],
    "feature_flag": ["flag_", "feature_", "enable_", "disable_", "toggle"],
    "logging": ["log_", "logging", "log_level", "sentry", "datadog"],
    "infrastructure": ["aws_", "gcp_", "azure_", "region", "bucket", "queue"],
    "general": [],
}


@dataclass
class ClassifiedKey:
    key: str
    category: str
    change_type: str  # "added", "removed", "changed"
    staging_value: Optional[str]
    production_value: Optional[str]

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "category": self.category,
            "change_type": self.change_type,
            "staging_value": self.staging_value,
            "production_value": self.production_value,
        }


@dataclass
class ClassifiedDiff:
    categories: Dict[str, List[ClassifiedKey]] = field(default_factory=dict)

    def all_keys(self) -> List[ClassifiedKey]:
        return [item for items in self.categories.values() for item in items]

    def keys_in_category(self, category: str) -> List[ClassifiedKey]:
        return self.categories.get(category, [])

    def as_dict(self) -> dict:
        return {
            cat: [k.as_dict() for k in keys]
            for cat, keys in self.categories.items()
        }


def _infer_category(key: str) -> str:
    lower = key.lower()
    for category, patterns in _CATEGORY_PATTERNS.items():
        if category == "general":
            continue
        if any(p in lower for p in patterns):
            return category
    return "general"


def classify_diff(result: DiffResult) -> ClassifiedDiff:
    """Classify every changed key in a DiffResult into a named category."""
    classified: Dict[str, List[ClassifiedKey]] = {cat: [] for cat in _CATEGORY_PATTERNS}

    for key in result.removed:
        cat = _infer_category(key)
        classified[cat].append(
            ClassifiedKey(key, cat, "removed", result.staging.get(key), None)
        )

    for key in result.added:
        cat = _infer_category(key)
        classified[cat].append(
            ClassifiedKey(key, cat, "added", None, result.production.get(key))
        )

    for key in result.changed:
        cat = _infer_category(key)
        classified[cat].append(
            ClassifiedKey(
                key, cat, "changed",
                result.staging.get(key),
                result.production.get(key),
            )
        )

    # Drop empty categories
    classified = {k: v for k, v in classified.items() if v}
    return ClassifiedDiff(categories=classified)
