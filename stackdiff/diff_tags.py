"""Tag and label diff results for grouping and filtering."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional

BUILTIN_TAG_RULES: Dict[str, List[str]] = {
    "database": ["db_", "database", "postgres", "mysql", "redis"],
    "auth": ["secret", "token", "password", "api_key", "auth"],
    "network": ["host", "port", "url", "endpoint", "addr"],
    "feature_flag": ["flag_", "feature_", "enable_", "disable_"],
    "logging": ["log_", "logging", "loglevel", "log_level"],
}


@dataclass
class TaggedKey:
    key: str
    tags: List[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {"key": self.key, "tags": self.tags}


@dataclass
class TaggedDiff:
    tagged_keys: List[TaggedKey] = field(default_factory=list)
    tag_index: Dict[str, List[str]] = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "tagged_keys": [tk.as_dict() for tk in self.tagged_keys],
            "tag_index": self.tag_index,
        }


def _infer_tags(key: str, rules: Optional[Dict[str, List[str]]] = None) -> List[str]:
    active = rules or BUILTIN_TAG_RULES
    key_lower = key.lower()
    return [
        tag
        for tag, patterns in active.items()
        if any(p in key_lower for p in patterns)
    ]


def tag_diff_keys(changed_keys: List[str], extra_rules: Optional[Dict[str, List[str]]] = None) -> TaggedDiff:
    rules = {**BUILTIN_TAG_RULES, **(extra_rules or {})}
    tagged_keys = [TaggedKey(key=k, tags=_infer_tags(k, rules)) for k in changed_keys]
    tag_index: Dict[str, List[str]] = {}
    for tk in tagged_keys:
        for tag in tk.tags:
            tag_index.setdefault(tag, []).append(tk.key)
    return TaggedDiff(tagged_keys=tagged_keys, tag_index=tag_index)


def filter_by_tag(tagged: TaggedDiff, tag: str) -> List[str]:
    return tagged.tag_index.get(tag, [])
