"""Tests for stackdiff.watch_handler."""

import pytest
from unittest.mock import patch, MagicMock
from stackdiff.watch_handler import _make_callback, start_watch


@pytest.fixture()
def tmp_yaml_pair(tmp_path):
    a = tmp_path / "a.yaml"
    b = tmp_path / "b.yaml"
    a.write_text("db_host: localhost\n")
    b.write_text("db_host: prod-server\n")
    return str(a), str(b)


def test_make_callback_returns_callable(tmp_yaml_pair):
    cb = _make_callback("text", None, [], [], True)
    assert callable(cb)


def test_callback_calls_pipeline_and_reporter(tmp_yaml_pair):
    a, b = tmp_yaml_pair
    with patch("stackdiff.watch_handler.run_pipeline") as mock_pipeline, \
         patch("stackdiff.watch_handler.generate_report") as mock_report:
        mock_pipeline.return_value = MagicMock()
        cb = _make_callback("text", None, [], [], True)
        cb(a, b)
        mock_pipeline.assert_called_once_with(
            a, b,
            include_patterns=[],
            exclude_patterns=[],
            mask_sensitive=True,
        )
        mock_report.assert_called_once()


def test_callback_handles_pipeline_error(tmp_yaml_pair, capsys):
    a, b = tmp_yaml_pair
    with patch("stackdiff.watch_handler.run_pipeline", side_effect=RuntimeError("boom")):
        cb = _make_callback("text", None, [], [], False)
        cb(a, b)  # should not raise
    captured = capsys.readouterr()
    assert "Error during diff" in captured.out


def test_start_watch_returns_watcher(tmp_yaml_pair):
    a, b = tmp_yaml_pair
    with patch("stackdiff.watch_handler.watch_configs") as mock_wc:
        mock_watcher = MagicMock()
        mock_wc.return_value = mock_watcher
        result = start_watch(a, b, fmt="json", interval=0.5)
        mock_wc.assert_called_once()
        assert result is mock_watcher


def test_start_watch_passes_interval(tmp_yaml_pair):
    a, b = tmp_yaml_pair
    with patch("stackdiff.watch_handler.watch_configs") as mock_wc:
        mock_wc.return_value = MagicMock()
        start_watch(a, b, interval=2.5)
        _, kwargs = mock_wc.call_args
        assert kwargs.get("interval") == 2.5 or mock_wc.call_args[0][3] == 2.5
