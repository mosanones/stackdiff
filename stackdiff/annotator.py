"""Annotate diff results with metadata such as change severity and categories."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from stackdiff.diff_engine import DiffResult

SEVERITY_PATTERNS = {
    "critical": ["secret", "password", "token", "key", "cert"],
    "high": ["database", "db_", "host", "port", "endpoint"],
    "medium": ["timeout", "retry", "limit", "max", "min"],
    "low": [],
}


@dataclass
class Annotation:
    key: str
    severity: str
    category: Optional[str]
    note: str


@dataclass
class AnnotatedDiff:
    diff: DiffResult
    annotations: List[Annotation] = field(default_factory=list)

    def by_severity(self, severity: str) -> List[Annotation]:
        return [a for a in self.annotations if a.severity == severity]


def _infer_severity(key: str) -> str:
    lower = key.lower()
    for severity, patterns in SEVERITY_PATTERNS.items():
        if any(p in lower for p in patterns):
            return severity
    return "low"


def _infer_category(key: str) -> Optional[str]:
    lower = key.lower()
    if any(p in lower for p in ["db", "database", "postgres", "mysql"]):
        return "database"
    if any(p in lower for p in ["host", "port", "endpoint", "url"]):
        return "network"
    if any(p in lower for p in ["secret", "password", "token", "key"]):
        return "security"
    return None


def annotate_diff(diff: DiffResult, extra_notes: Optional[Dict[str, str]] = None) -> AnnotatedDiff:
    """Attach severity and category annotations to each changed key."""
    extra_notes = extra_notes or {}
    annotations = []
    all_keys = set(diff.removed) | set(diff.added) | set(diff.changed)
    for key in sorted(all_keys):
        severity = _infer_severity(key)
        category = _infer_category(key)
        note = extra_notes.get(key, "")
        annotations.append(Annotation(key=key, severity=severity, category=category, note=note))
    return AnnotatedDiff(diff=diff, annotations=annotations)
