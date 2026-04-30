"""Compare two snapshots directly and produce a DiffResult."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from stackdiff.snapshotter import load_snapshot, list_snapshots
from stackdiff.diff_engine import DiffResult, diff_configs
from stackdiff.masker import mask_config
from stackdiff.annotator import annotate, AnnotatedDiff
from stackdiff.scorer import score_annotated, DiffScore


@dataclass
class SnapshotComparison:
    left_name: str
    right_name: str
    diff: DiffResult
    annotated: AnnotatedDiff
    score: DiffScore
    masked: bool = False

    def as_dict(self) -> dict:
        return {
            "left_name": self.left_name,
            "right_name": self.right_name,
            "has_diff": self.diff.has_diff(),
            "added": self.diff.added,
            "removed": self.diff.removed,
            "changed": self.diff.changed,
            "score": self.score.as_dict(),
            "masked": self.masked,
        }


def compare_snapshots(
    left_name: str,
    right_name: str,
    snapshot_dir: Optional[str] = None,
    mask_secrets: bool = True,
) -> SnapshotComparison:
    """Load two named snapshots and diff them."""
    kwargs = {"snapshot_dir": snapshot_dir} if snapshot_dir else {}
    left_cfg = load_snapshot(left_name, **kwargs)
    right_cfg = load_snapshot(right_name, **kwargs)

    if mask_secrets:
        left_cfg = mask_config(left_cfg)
        right_cfg = mask_config(right_cfg)

    result = diff_configs(left_cfg, right_cfg, label_a=left_name, label_b=right_name)
    annotated = annotate(result)
    score = score_annotated(annotated)

    return SnapshotComparison(
        left_name=left_name,
        right_name=right_name,
        diff=result,
        annotated=annotated,
        score=score,
        masked=mask_secrets,
    )


def list_comparable_snapshots(snapshot_dir: Optional[str] = None) -> list[str]:
    """Return sorted list of available snapshot names."""
    kwargs = {"snapshot_dir": snapshot_dir} if snapshot_dir else {}
    return sorted(list_snapshots(**kwargs))
