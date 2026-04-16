"""Masking sensitive keys before output."""

import re
from typing import Dict, List

DEFAULT_PATTERNS = [
    r".*password.*",
    r".*secret.*",
    r".*token.*",
    r".*api[_.]?key.*",
    r".*private[_.]?key.*",
    r".*credentials.*",
]

MASK_VALUE = "***"


def _is_sensitive(key: str, patterns: List[str]) -> bool:
    """Return True if key matches any sensitive pattern (case-insensitive)."""
    lower = key.lower()
    return any(re.fullmatch(p, lower) for p in patterns)


def mask_config(
    config: Dict[str, str],
    patterns: List[str] | None = None,
    extra_patterns: List[str] | None = None,
) -> Dict[str, str]:
    """Return a copy of config with sensitive values replaced by MASK_VALUE.

    Args:
        config: Flat key->value mapping.
        patterns: Override default patterns entirely when provided.
        extra_patterns: Additional patterns appended to the defaults.
    """
    active = list(patterns if patterns is not None else DEFAULT_PATTERNS)
    if extra_patterns:
        active.extend(extra_patterns)

    return {
        k: (MASK_VALUE if _is_sensitive(k, active) else v)
        for k, v in config.items()
    }


def mask_diff_values(
    added: Dict[str, str],
    removed: Dict[str, str],
    changed: Dict[str, tuple],
    patterns: List[str] | None = None,
    extra_patterns: List[str] | None = None,
) -> tuple:
    """Mask sensitive values inside diff buckets.

    Returns (masked_added, masked_removed, masked_changed).
    """
    active = list(patterns if patterns is not None else DEFAULT_PATTERNS)
    if extra_patterns:
        active.extend(extra_patterns)

    m_added = {k: (MASK_VALUE if _is_sensitive(k, active) else v) for k, v in added.items()}
    m_removed = {k: (MASK_VALUE if _is_sensitive(k, active) else v) for k, v in removed.items()}
    m_changed = {
        k: (
            (MASK_VALUE, MASK_VALUE) if _is_sensitive(k, active) else (old, new)
        )
        for k, (old, new) in changed.items()
    }
    return m_added, m_removed, m_changed
