"""diff_explainer.py — generates human-readable explanations for diff changes."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional

from stackdiff.diff_engine import DiffResult
from stackdiff.annotator import AnnotatedDiff, Annotation


@dataclass
class Explanation:
    key: str
    change_type: str  # 'added', 'removed', 'changed'
    old_value: Optional[str]
    new_value: Optional[str]
    severity: str
    category: str
    message: str

    def as_dict(self) -> Dict:
        return {
            "key": self.key,
            "change_type": self.change_type,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "severity": self.severity,
            "category": self.category,
            "message": self.message,
        }


@dataclass
class DiffExplanation:
    explanations: List[Explanation] = field(default_factory=list)

    def as_dict(self) -> Dict:
        return {"explanations": [e.as_dict() for e in self.explanations]}


def _build_message(key: str, change_type: str, old_val: Optional[str], new_val: Optional[str], severity: str) -> str:
    if change_type == "removed":
        return f"Key '{key}' was removed. This may break dependents expecting this value."
    if change_type == "added":
        return f"Key '{key}' is newly introduced with value '{new_val}'."
    prefix = "[CRITICAL] " if severity == "critical" else ""
    return (
        f"{prefix}Key '{key}' changed from '{old_val}' to '{new_val}'."
    )


def explain_annotated(annotated: AnnotatedDiff) -> DiffExplanation:
    """Produce plain-language explanations from an AnnotatedDiff."""
    explanations: List[Explanation] = []

    result = annotated.diff

    for key, val in result.removed.items():
        ann: Annotation = annotated.annotations.get(key, Annotation(key=key, severity="low", category="general"))
        explanations.append(Explanation(
            key=key,
            change_type="removed",
            old_value=str(val),
            new_value=None,
            severity=ann.severity,
            category=ann.category,
            message=_build_message(key, "removed", str(val), None, ann.severity),
        ))

    for key, val in result.added.items():
        ann = annotated.annotations.get(key, Annotation(key=key, severity="low", category="general"))
        explanations.append(Explanation(
            key=key,
            change_type="added",
            old_value=None,
            new_value=str(val),
            severity=ann.severity,
            category=ann.category,
            message=_build_message(key, "added", None, str(val), ann.severity),
        ))

    for key, (old_val, new_val) in result.changed.items():
        ann = annotated.annotations.get(key, Annotation(key=key, severity="low", category="general"))
        explanations.append(Explanation(
            key=key,
            change_type="changed",
            old_value=str(old_val),
            new_value=str(new_val),
            severity=ann.severity,
            category=ann.category,
            message=_build_message(key, "changed", str(old_val), str(new_val), ann.severity),
        ))

    explanations.sort(key=lambda e: ("critical", "high", "medium", "low").index(e.severity)
                      if e.severity in ("critical", "high", "medium", "low") else 99)
    return DiffExplanation(explanations=explanations)
