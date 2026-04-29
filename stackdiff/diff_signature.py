"""diff_signature.py — generate a stable fingerprint for a DiffResult.

A signature is a short hash that uniquely identifies the *shape* of a diff
(which keys changed and in which direction) independently of the actual values.
This lets callers detect whether two diffs represent the same structural change
even when secret values differ.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Optional

from stackdiff.diff_engine import DiffResult


@dataclass
class DiffSignature:
    """Fingerprint for a DiffResult."""
    hexdigest: str
    key_count: int
    removed_count: int
    added_count: int
    changed_count: int

    def short(self, length: int = 8) -> str:
        """Return a short version of the hex digest."""
        return self.hexdigest[:length]

    def as_dict(self) -> dict:
        return {
            "hexdigest": self.hexdigest,
            "short": self.short(),
            "key_count": self.key_count,
            "removed_count": self.removed_count,
            "added_count": self.added_count,
            "changed_count": self.changed_count,
        }


def _classify_keys(result: DiffResult) -> tuple[list[str], list[str], list[str]]:
    """Return (removed, added, changed) key lists from a DiffResult."""
    removed: list[str] = []
    added: list[str] = []
    changed: list[str] = []

    all_keys = sorted(set(result.left) | set(result.right))
    for key in all_keys:
        in_left = key in result.left
        in_right = key in result.right
        if in_left and not in_right:
            removed.append(key)
        elif in_right and not in_left:
            added.append(key)
        elif result.left.get(key) != result.right.get(key):
            changed.append(key)

    return removed, added, changed


def sign_diff(result: DiffResult, algorithm: str = "sha256") -> DiffSignature:
    """Compute a stable signature for *result*.

    The hash is derived from the sorted lists of removed, added, and changed
    key names only — values are intentionally excluded so that secrets do not
    leak into the fingerprint.
    """
    removed, added, changed = _classify_keys(result)

    payload = json.dumps(
        {"removed": removed, "added": added, "changed": changed},
        sort_keys=True,
    ).encode()

    h = hashlib.new(algorithm, payload)

    return DiffSignature(
        hexdigest=h.hexdigest(),
        key_count=len(set(result.left) | set(result.right)),
        removed_count=len(removed),
        added_count=len(added),
        changed_count=len(changed),
    )


def signatures_match(a: DiffSignature, b: DiffSignature) -> bool:
    """Return True when two signatures represent the same structural diff."""
    return a.hexdigest == b.hexdigest
