"""diff_templater.py — render diff results using named output templates."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from stackdiff.diff_engine import DiffResult
from stackdiff.annotator import AnnotatedDiff


_BUILTIN_TEMPLATES: Dict[str, str] = {
    "minimal": "{label_a} vs {label_b}: {total} change(s)",
    "compact": "[{label_a}/{label_b}] +{added} -{removed} ~{changed}",
    "verbose": (
        "=== Diff: {label_a} → {label_b} ===\n"
        "  Added   : {added}\n"
        "  Removed : {removed}\n"
        "  Changed : {changed}\n"
        "  Total   : {total}"
    ),
    "ci": "DIFF result={label} added={added} removed={removed} changed={changed} total={total}",
}


@dataclass
class TemplateResult:
    template_name: str
    rendered: str
    context: Dict[str, object] = field(default_factory=dict)

    def __str__(self) -> str:
        return self.rendered


def _risk_label(total: int) -> str:
    if total == 0:
        return "clean"
    if total <= 3:
        return "low"
    if total <= 8:
        return "moderate"
    return "high"


def _build_context(
    result: DiffResult,
    label_a: str = "base",
    label_b: str = "compare",
) -> Dict[str, object]:
    added = len(result.added)
    removed = len(result.removed)
    changed = len(result.changed)
    total = added + removed + changed
    return {
        "label_a": label_a,
        "label_b": label_b,
        "added": added,
        "removed": removed,
        "changed": changed,
        "total": total,
        "label": _risk_label(total),
    }


def list_templates(extra: Optional[Dict[str, str]] = None) -> List[str]:
    """Return names of all available templates."""
    names = list(_BUILTIN_TEMPLATES.keys())
    if extra:
        names += [k for k in extra if k not in names]
    return sorted(names)


def render_template(
    result: DiffResult,
    template_name: str = "compact",
    label_a: str = "base",
    label_b: str = "compare",
    extra_templates: Optional[Dict[str, str]] = None,
) -> TemplateResult:
    """Render *result* with the named template and return a TemplateResult."""
    registry = {**_BUILTIN_TEMPLATES, **(extra_templates or {})}
    if template_name not in registry:
        available = ", ".join(sorted(registry))
        raise KeyError(f"Unknown template '{template_name}'. Available: {available}")
    ctx = _build_context(result, label_a=label_a, label_b=label_b)
    rendered = registry[template_name].format(**ctx)
    return TemplateResult(template_name=template_name, rendered=rendered, context=ctx)
