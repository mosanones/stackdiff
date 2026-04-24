"""Merge two DiffResult objects into a unified view across multiple environment pairs."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from stackdiff.diff_engine import DiffResult


@dataclass
class MergedDiff:
    """Combined diff across multiple labelled environment pairs."""
    labels: List[str]
    # key -> list of (old, new) per label; None means key absent in that pair
    merged: Dict[str, List[Optional[Tuple[Optional[str], Optional[str]]]]]

    def as_dict(self) -> dict:
        return {
            "labels": self.labels,
            "merged": {
                k: [
                    {"old": old, "new": new} if entry is not None else None
                    for entry, (old, new) in (
                        (entry, entry) for entry in v
                    )
                ]
                for k, v in self.merged.items()
            },
        }

    def all_keys(self) -> List[str]:
        return sorted(self.merged.keys())

    def keys_changed_in_all(self) -> List[str]:
        """Return keys that differ in every label."""
        return [
            k for k, entries in self.merged.items()
            if all(e is not None and e[0] != e[1] for e in entries)
        ]


def merge_diffs(labelled_diffs: List[Tuple[str, DiffResult]]) -> MergedDiff:
    """Merge a list of (label, DiffResult) pairs into a MergedDiff.

    For each key that appears in *any* diff, record (old, new) per label.
    If a key is absent from a particular diff entirely, record None.
    """
    labels = [label for label, _ in labelled_diffs]
    all_keys: set = set()
    for _, dr in labelled_diffs:
        all_keys.update(dr.removed.keys())
        all_keys.update(dr.added.keys())
        all_keys.update(dr.changed.keys())

    merged: Dict[str, List[Optional[Tuple[Optional[str], Optional[str]]]]] = {}
    for key in sorted(all_keys):
        entries: List[Optional[Tuple[Optional[str], Optional[str]]]] = []
        for _, dr in labelled_diffs:
            if key in dr.changed:
                old_val, new_val = dr.changed[key]
                entries.append((str(old_val), str(new_val)))
            elif key in dr.removed:
                entries.append((str(dr.removed[key]), None))
            elif key in dr.added:
                entries.append((None, str(dr.added[key])))
            else:
                entries.append(None)
        merged[key] = entries

    return MergedDiff(labels=labels, merged=merged)
