"""Tests for stackdiff.watcher."""

import os
import time
import threading
import pytest
from unittest.mock import MagicMock, patch
from stackdiff.watcher import ConfigWatcher, watch_configs


@pytest.fixture()
def tmp_configs(tmp_path):
    a = tmp_path / "staging.yaml"
    b = tmp_path / "prod.yaml"
    a.write_text("key: value\n")
    b.write_text("key: value\n")
    return str(a), str(b)


def test_watch_configs_returns_watcher(tmp_configs):
    a, b = tmp_configs
    cb = MagicMock()
    watcher = watch_configs(a, b, cb, interval=0.05)
    assert isinstance(watcher, ConfigWatcher)
    assert watcher.path_a == a
    assert watcher.path_b == b


def test_no_callback_when_files_unchanged(tmp_configs):
    a, b = tmp_configs
    cb = MagicMock()
    watcher = ConfigWatcher(a, b, cb, interval=0.05)
    watcher.start(max_iterations=3)
    cb.assert_not_called()


def test_callback_triggered_on_change(tmp_configs):
    a, b = tmp_configs
    cb = MagicMock()
    watcher = ConfigWatcher(a, b, cb, interval=0.05)

    def modify_after_delay():
        time.sleep(0.08)
        with open(a, "w") as f:
            f.write("key: changed\n")

    t = threading.Thread(target=modify_after_delay)
    t.start()
    watcher.start(max_iterations=5)
    t.join()
    cb.assert_called()
    args = cb.call_args[0]
    assert args[0] == a
    assert args[1] == b


def test_stop_halts_watcher(tmp_configs):
    a, b = tmp_configs
    cb = MagicMock()
    watcher = ConfigWatcher(a, b, cb, interval=0.05)

    def stopper():
        time.sleep(0.12)
        watcher.stop()

    t = threading.Thread(target=stopper)
    t.start()
    watcher.start()  # runs until stop() is called
    t.join()
    assert not watcher._running


def test_missing_file_does_not_raise(tmp_configs):
    a, b = tmp_configs
    cb = MagicMock()
    os.remove(b)
    watcher = ConfigWatcher(a, b, cb, interval=0.05)
    # Should not raise even if file disappears
    watcher.start(max_iterations=2)
    cb.assert_not_called()
