"""Tests for the annotator pipeline module and formatter."""
import json
import pytest

from stackdiff.diff_engine import DiffResult
from stackdiff.diff_annotator_pipeline import (
    AnnotatorPipelineResult,
    run_annotator_pipeline,
)
from stackdiff.annotator_pipeline_formatter import (
    format_pipeline_text,
    format_pipeline_json,
    format_pipeline_output,
)


@pytest.fixture
def simple_diff():
    return DiffResult(
        label_a="staging",
        label_b="production",
        removed={"db.password": "secret123"},
        added={"db.password": "newsecret"},
        unchanged={"app.debug": "false"},
    )


@pytest.fixture
def empty_diff():
    return DiffResult(
        label_a="staging",
        label_b="production",
        removed={},
        added={},
        unchanged={"app.name": "myapp"},
    )


def test_run_annotator_pipeline_returns_result(simple_diff):
    result = run_annotator_pipeline(simple_diff)
    assert isinstance(result, AnnotatorPipelineResult)


def test_pipeline_result_has_annotated(simple_diff):
    result = run_annotator_pipeline(simple_diff)
    assert result.annotated is not None
    assert len(result.annotated.annotations) > 0


def test_pipeline_result_has_score(simple_diff):
    result = run_annotator_pipeline(simple_diff)
    assert isinstance(result.score.score, (int, float))


def test_pipeline_result_has_summary(simple_diff):
    result = run_annotator_pipeline(simple_diff)
    assert result.summary.total_changes >= 1


def test_pipeline_result_has_recommendations(simple_diff):
    result = run_annotator_pipeline(simple_diff)
    assert result.recommendations is not None


def test_as_dict_keys(simple_diff):
    result = run_annotator_pipeline(simple_diff)
    d = result.as_dict()
    assert set(d.keys()) == {"score", "summary", "recommendations", "annotations"}


def test_as_dict_annotations_list(simple_diff):
    result = run_annotator_pipeline(simple_diff)
    d = result.as_dict()
    assert isinstance(d["annotations"], list)
    if d["annotations"]:
        ann = d["annotations"][0]
        assert "key" in ann and "severity" in ann and "category" in ann


def test_format_pipeline_text_contains_header(simple_diff):
    result = run_annotator_pipeline(simple_diff)
    text = format_pipeline_text(result)
    assert "Annotator Pipeline Report" in text


def test_format_pipeline_text_shows_score(simple_diff):
    result = run_annotator_pipeline(simple_diff)
    text = format_pipeline_text(result)
    assert "Risk Score" in text


def test_format_pipeline_json_is_valid(simple_diff):
    result = run_annotator_pipeline(simple_diff)
    raw = format_pipeline_json(result)
    parsed = json.loads(raw)
    assert "score" in parsed


def test_format_pipeline_output_text(simple_diff):
    result = run_annotator_pipeline(simple_diff)
    out = format_pipeline_output(result, fmt="text")
    assert isinstance(out, str)
    assert "Annotator Pipeline Report" in out


def test_format_pipeline_output_json(simple_diff):
    result = run_annotator_pipeline(simple_diff)
    out = format_pipeline_output(result, fmt="json")
    parsed = json.loads(out)
    assert "annotations" in parsed


def test_empty_diff_zero_changes(empty_diff):
    result = run_annotator_pipeline(empty_diff)
    assert result.summary.total_changes == 0
    assert result.annotated.annotations == []
