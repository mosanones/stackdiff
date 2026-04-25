"""Tests for stackdiff.diff_templater."""

from __future__ import annotations

import pytest

from stackdiff.diff_engine import DiffResult
from stackdiff.diff_templater import (
    TemplateResult,
    list_templates,
    render_template,
    _build_context,
    _risk_label,
)


@pytest.fixture()
def no_diff() -> DiffResult:
    return DiffResult(added={}, removed={}, changed={})


@pytest.fixture()
def small_diff() -> DiffResult:
    return DiffResult(
        added={"app.port": "9000"},
        removed={"app.debug": "true"},
        changed={"db.host": ("localhost", "prod-db")},
    )


# --- _risk_label ---

def test_risk_label_clean():
    assert _risk_label(0) == "clean"

def test_risk_label_low():
    assert _risk_label(2) == "low"

def test_risk_label_moderate():
    assert _risk_label(5) == "moderate"

def test_risk_label_high():
    assert _risk_label(10) == "high"


# --- _build_context ---

def test_build_context_counts(small_diff):
    ctx = _build_context(small_diff, label_a="staging", label_b="prod")
    assert ctx["added"] == 1
    assert ctx["removed"] == 1
    assert ctx["changed"] == 1
    assert ctx["total"] == 3

def test_build_context_labels(small_diff):
    ctx = _build_context(small_diff, label_a="A", label_b="B")
    assert ctx["label_a"] == "A"
    assert ctx["label_b"] == "B"

def test_build_context_no_diff_clean(no_diff):
    ctx = _build_context(no_diff)
    assert ctx["total"] == 0
    assert ctx["label"] == "clean"


# --- list_templates ---

def test_list_templates_includes_builtins():
    names = list_templates()
    assert "compact" in names
    assert "minimal" in names
    assert "verbose" in names
    assert "ci" in names

def test_list_templates_includes_extra():
    names = list_templates(extra={"custom": "{total}"})
    assert "custom" in names

def test_list_templates_sorted():
    names = list_templates()
    assert names == sorted(names)


# --- render_template ---

def test_render_returns_template_result(small_diff):
    result = render_template(small_diff)
    assert isinstance(result, TemplateResult)

def test_render_compact_contains_counts(small_diff):
    result = render_template(small_diff, template_name="compact")
    assert "+1" in result.rendered
    assert "-1" in result.rendered

def test_render_minimal_contains_total(small_diff):
    result = render_template(small_diff, template_name="minimal", label_a="s", label_b="p")
    assert "3" in result.rendered
    assert "s" in result.rendered

def test_render_verbose_multiline(small_diff):
    result = render_template(small_diff, template_name="verbose")
    assert "\n" in result.rendered
    assert "Added" in result.rendered

def test_render_ci_format(small_diff):
    result = render_template(small_diff, template_name="ci")
    assert "DIFF" in result.rendered
    assert "total=3" in result.rendered

def test_render_unknown_template_raises(small_diff):
    with pytest.raises(KeyError, match="Unknown template"):
        render_template(small_diff, template_name="nonexistent")

def test_render_custom_template(small_diff):
    result = render_template(
        small_diff,
        template_name="custom",
        extra_templates={"custom": "changes={total}"},
    )
    assert result.rendered == "changes=3"

def test_render_str_dunder(small_diff):
    result = render_template(small_diff, template_name="minimal")
    assert str(result) == result.rendered

def test_render_context_stored(small_diff):
    result = render_template(small_diff, template_name="compact", label_a="X", label_b="Y")
    assert result.context["label_a"] == "X"
    assert result.context["added"] == 1
