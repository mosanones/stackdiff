"""File watcher that triggers re-comparison when config files change."""

import time
import os
from typing import Callable, Optional


class ConfigWatcher:
    """Watches two config files and calls a callback when either changes."""

    def __init__(
        self,
        path_a: str,
        path_b: str,
        callback: Callable[[str, str], None],
        interval: float = 1.0,
    ):
        self.path_a = path_a
        self.path_b = path_b
        self.callback = callback
        self.interval = interval
        self._last_mtime: dict[str, Optional[float]] = {
            path_a: None,
            path_b: None,
        }
        self._running = False

    def _get_mtime(self, path: str) -> Optional[float]:
        try:
            return os.path.getmtime(path)
        except FileNotFoundError:
            return None

    def _has_changed(self) -> bool:
        changed = False
        for path in (self.path_a, self.path_b):
            mtime = self._get_mtime(path)
            if mtime != self._last_mtime[path]:
                self._last_mtime[path] = mtime
                changed = True
        return changed

    def start(self, max_iterations: Optional[int] = None) -> None:
        """Start watching. Runs until stop() is called or max_iterations reached."""
        self._running = True
        # Seed initial mtimes without triggering callback
        for path in (self.path_a, self.path_b):
            self._last_mtime[path] = self._get_mtime(path)

        iterations = 0
        while self._running:
            if max_iterations is not None and iterations >= max_iterations:
                break
            time.sleep(self.interval)
            if self._has_changed():
                self.callback(self.path_a, self.path_b)
            iterations += 1

    def stop(self) -> None:
        self._running = False


def watch_configs(
    path_a: str,
    path_b: str,
    callback: Callable[[str, str], None],
    interval: float = 1.0,
) -> ConfigWatcher:
    """Convenience factory — creates and returns a ConfigWatcher (not yet started)."""
    return ConfigWatcher(path_a, path_b, callback, interval)
