import pytest
from stackdiff.diff_engine import DiffResult
from stackdiff.annotator import annotate_diff, _infer_severity, _infer_category, AnnotatedDiff


@pytest.fixture
def sample_diff():
    return DiffResult(
        removed={"db_password": "old"},
        added={"api_endpoint": "https://new.example.com"},
        changed={"max_retries": ("3", "5"), "app_secret_key": ("aaa", "bbb")},
    )


def test_annotate_returns_annotated_diff(sample_diff):
    result = annotate_diff(sample_diff)
    assert isinstance(result, AnnotatedDiff)
    assert result.diff is sample_diff


def test_all_changed_keys_annotated(sample_diff):
    result = annotate_diff(sample_diff)
    keys = {a.key for a in result.annotations}
    assert "db_password" in keys
    assert "api_endpoint" in keys
    assert "max_retries" in keys
    assert "app_secret_key" in keys


def test_severity_critical_for_password(sample_diff):
    result = annotate_diff(sample_diff)
    ann = next(a for a in result.annotations if a.key == "db_password")
    assert ann.severity == "critical"


def test_severity_high_for_endpoint(sample_diff):
    result = annotate_diff(sample_diff)
    ann = next(a for a in result.annotations if a.key == "api_endpoint")
    assert ann.severity == "high"


def test_severity_medium_for_retries(sample_diff):
    result = annotate_diff(sample_diff)
    ann = next(a for a in result.annotations if a.key == "max_retries")
    assert ann.severity == "medium"


def test_category_security_for_secret(sample_diff):
    result = annotate_diff(sample_diff)
    ann = next(a for a in result.annotations if a.key == "app_secret_key")
    assert ann.category == "security"


def test_extra_notes_attached(sample_diff):
    notes = {"max_retries": "Increased for resilience"}
    result = annotate_diff(sample_diff, extra_notes=notes)
    ann = next(a for a in result.annotations if a.key == "max_retries")
    assert ann.note == "Increased for resilience"


def test_by_severity_filters(sample_diff):
    result = annotate_diff(sample_diff)
    critical = result.by_severity("critical")
    assert all(a.severity == "critical" for a in critical)


def test_infer_severity_unknown_key():
    assert _infer_severity("some_random_flag") == "low"


def test_infer_category_network():
    assert _infer_category("service_host") == "network"


def test_infer_category_unknown():
    assert _infer_category("log_level") is None
