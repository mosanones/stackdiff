"""Tests for stackdiff.notifier."""
from __future__ import annotations

import json
import os
from unittest.mock import MagicMock, patch

import pytest

from stackdiff.alerter import Alert
from stackdiff.notifier import NotifyResult, dispatch, notify_file, notify_stdout, notify_webhook


@pytest.fixture()
def alerts() -> list[Alert]:
    return [
        Alert(rule="high_score", level="high", message="Score exceeded threshold"),
        Alert(rule="critical_keys", level="critical", message="password changed"),
    ]


@pytest.fixture()
def empty_alerts() -> list[Alert]:
    return []


def test_notify_result_as_dict():
    r = NotifyResult("stdout", True, "ok")
    d = r.as_dict()
    assert d == {"channel": "stdout", "success": True, "message": "ok"}


def test_notify_stdout_no_alerts(empty_alerts, capsys):
    result = notify_stdout(empty_alerts)
    assert result.success
    assert "No alerts" in capsys.readouterr().out


def test_notify_stdout_with_alerts(alerts, capsys):
    result = notify_stdout(alerts)
    out = capsys.readouterr().out
    assert result.success
    assert "[HIGH]" in out
    assert "[CRITICAL]" in out
    assert "2 alert(s)" in result.message


def test_notify_file_writes_json(alerts, tmp_path):
    path = str(tmp_path / "alerts.json")
    result = notify_file(alerts, path)
    assert result.success
    assert os.path.exists(path)
    with open(path) as fh:
        data = json.load(fh)
    assert len(data) == 2
    assert data[0]["rule"] == "high_score"


def test_notify_file_empty_alerts(empty_alerts, tmp_path):
    path = str(tmp_path / "empty.json")
    result = notify_file(empty_alerts, path)
    assert result.success
    with open(path) as fh:
        assert json.load(fh) == []


def test_notify_file_bad_path(alerts):
    result = notify_file(alerts, "/nonexistent_dir/alerts.json")
    assert not result.success
    assert result.channel == "file"


def test_notify_webhook_success(alerts):
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("urllib.request.urlopen", return_value=mock_resp):
        result = notify_webhook(alerts, "http://example.com/hook")
    assert result.success
    assert "200" in result.message


def test_notify_webhook_failure(alerts):
    with patch("urllib.request.urlopen", side_effect=OSError("connection refused")):
        result = notify_webhook(alerts, "http://example.com/hook")
    assert not result.success
    assert "connection refused" in result.message


def test_dispatch_stdout_only(alerts, capsys):
    results = dispatch(alerts, stdout=True)
    assert len(results) == 1
    assert results[0].channel == "stdout"


def test_dispatch_all_channels(alerts, tmp_path):
    path = str(tmp_path / "out.json")
    mock_resp = MagicMock(status=200)
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("urllib.request.urlopen", return_value=mock_resp):
        results = dispatch(alerts, stdout=True, file_path=path, webhook_url="http://x.com")
    channels = {r.channel for r in results}
    assert channels == {"stdout", "file", "webhook"}
