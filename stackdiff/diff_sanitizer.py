"""diff_sanitizer.py — strip or redact problematic values before diffing."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_DEFAULT_STRIP_PATTERNS: List[str] = [
    r"\s+",          # leading/trailing whitespace (applied via strip)
]

_DEFAULT_REDACT_PATTERNS: List[str] = [
    r"^(https?://)([^@]+@)",  # embedded credentials in URLs
]

_PLACEHOLDER = "<redacted>"


@dataclass
class SanitizeOptions:
    strip_whitespace: bool = True
    lowercase_keys: bool = False
    redact_url_credentials: bool = True
    extra_redact_patterns: List[str] = field(default_factory=list)
    drop_null_values: bool = False


@dataclass
class SanitizeResult:
    original: Dict[str, object]
    sanitized: Dict[str, object]
    redacted_keys: List[str] = field(default_factory=list)
    dropped_keys: List[str] = field(default_factory=list)

    def was_modified(self) -> bool:
        return bool(self.redacted_keys or self.dropped_keys or self.original != self.sanitized)

    def as_dict(self) -> dict:
        return {
            "redacted_keys": self.redacted_keys,
            "dropped_keys": self.dropped_keys,
            "was_modified": self.was_modified(),
        }


def _build_redact_patterns(opts: SanitizeOptions) -> List[re.Pattern]:
    patterns = []
    if opts.redact_url_credentials:
        for p in _DEFAULT_REDACT_PATTERNS:
            patterns.append(re.compile(p))
    for p in opts.extra_redact_patterns:
        patterns.append(re.compile(p))
    return patterns


def _redact_value(value: str, patterns: List[re.Pattern]) -> Optional[str]:
    """Return redacted string if any pattern matches, else None."""
    for pat in patterns:
        if pat.search(value):
            return pat.sub(lambda m: m.group(1) + _PLACEHOLDER if m.lastindex else _PLACEHOLDER, value)
    return None


def sanitize_config(cfg: Dict[str, object], opts: Optional[SanitizeOptions] = None) -> SanitizeResult:
    """Return a sanitized copy of *cfg* according to *opts*."""
    if opts is None:
        opts = SanitizeOptions()

    redact_patterns = _build_redact_patterns(opts)
    sanitized: Dict[str, object] = {}
    redacted_keys: List[str] = []
    dropped_keys: List[str] = []

    for raw_key, value in cfg.items():
        key = raw_key.lower() if opts.lowercase_keys else raw_key

        if opts.drop_null_values and value is None:
            dropped_keys.append(key)
            continue

        if isinstance(value, str):
            processed = value.strip() if opts.strip_whitespace else value
            redacted = _redact_value(processed, redact_patterns)
            if redacted is not None:
                sanitized[key] = redacted
                redacted_keys.append(key)
            else:
                sanitized[key] = processed
        else:
            sanitized[key] = value

    return SanitizeResult(
        original=dict(cfg),
        sanitized=sanitized,
        redacted_keys=redacted_keys,
        dropped_keys=dropped_keys,
    )
