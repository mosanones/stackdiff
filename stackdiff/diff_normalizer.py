"""Normalize flat config dicts before diffing: type coercion, whitespace trimming, and value aliasing."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


_TRUTHY = {"true", "yes", "1", "on"}
_FALSY = {"false", "no", "0", "off"}


@dataclass
class NormalizeOptions:
    strip_whitespace: bool = True
    coerce_booleans: bool = True
    coerce_numbers: bool = True
    lowercase_keys: bool = False
    aliases: Dict[str, str] = field(default_factory=dict)  # old_key -> canonical_key


@dataclass
class NormalizeResult:
    config: Dict[str, Any]
    changes: List[str] = field(default_factory=list)

    def was_modified(self) -> bool:
        return bool(self.changes)


def _coerce_value(key: str, value: Any, opts: NormalizeOptions) -> tuple[Any, Optional[str]]:
    """Return (new_value, change_description | None)."""
    if not isinstance(value, str):
        return value, None

    original = value

    if opts.strip_whitespace:
        value = value.strip()

    if opts.coerce_booleans and value.lower() in _TRUTHY:
        value = True
    elif opts.coerce_booleans and value.lower() in _FALSY:
        value = False
    elif opts.coerce_numbers:
        try:
            value = int(value)
        except ValueError:
            try:
                value = float(value)
            except ValueError:
                pass

    if value != original:
        return value, f"{key}: {original!r} -> {value!r}"
    return value, None


def normalize_config(cfg: Dict[str, Any], opts: Optional[NormalizeOptions] = None) -> NormalizeResult:
    """Return a new normalized config dict along with a log of applied changes."""
    if opts is None:
        opts = NormalizeOptions()

    result: Dict[str, Any] = {}
    changes: List[str] = []

    for raw_key, value in cfg.items():
        key = raw_key.lower() if opts.lowercase_keys else raw_key

        if key in opts.aliases:
            new_key = opts.aliases[key]
            changes.append(f"alias: {key} -> {new_key}")
            key = new_key

        coerced, change = _coerce_value(key, value, opts)
        if change:
            changes.append(change)

        result[key] = coerced

    return NormalizeResult(config=result, changes=changes)


def normalize_pair(
    left: Dict[str, Any],
    right: Dict[str, Any],
    opts: Optional[NormalizeOptions] = None,
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    """Normalize both sides of a diff pair using the same options."""
    return normalize_config(left, opts).config, normalize_config(right, opts).config
