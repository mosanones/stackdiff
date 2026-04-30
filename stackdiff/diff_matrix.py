"""diff_matrix.py — build a pairwise comparison matrix across multiple environments."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from stackdiff.diff_engine import DiffResult, diff_configs


@dataclass
class MatrixCell:
    left: str
    right: str
    added: int
    removed: int
    changed: int

    @property
    def total(self) -> int:
        return self.added + self.removed + self.changed

    @property
    def has_diff(self) -> bool:
        return self.total > 0

    def as_dict(self) -> dict:
        return {
            "left": self.left,
            "right": self.right,
            "added": self.added,
            "removed": self.removed,
            "changed": self.changed,
            "total": self.total,
            "has_diff": self.has_diff,
        }


@dataclass
class DiffMatrix:
    env_names: List[str]
    cells: List[MatrixCell] = field(default_factory=list)

    def get_cell(self, left: str, right: str) -> Optional[MatrixCell]:
        for c in self.cells:
            if c.left == left and c.right == right:
                return c
        return None

    def pairs_with_diff(self) -> List[MatrixCell]:
        return [c for c in self.cells if c.has_diff]

    def as_dict(self) -> dict:
        return {
            "env_names": self.env_names,
            "cells": [c.as_dict() for c in self.cells],
        }


def _count_changes(result: DiffResult) -> Tuple[int, int, int]:
    added = sum(1 for v in result.values() if v[0] is None and v[1] is not None)
    removed = sum(1 for v in result.values() if v[0] is not None and v[1] is None)
    changed = sum(
        1 for v in result.values()
        if v[0] is not None and v[1] is not None and v[0] != v[1]
    )
    return added, removed, changed


def build_matrix(envs: Dict[str, dict]) -> DiffMatrix:
    """Build a pairwise diff matrix for all combinations of environments."""
    names = list(envs.keys())
    matrix = DiffMatrix(env_names=names)
    for i, left in enumerate(names):
        for right in names[i + 1 :]:
            result = diff_configs(envs[left], envs[right])
            added, removed, changed = _count_changes(result)
            matrix.cells.append(
                MatrixCell(
                    left=left,
                    right=right,
                    added=added,
                    removed=removed,
                    changed=changed,
                )
            )
    return matrix
