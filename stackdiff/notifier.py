"""Notifier: send alert summaries to output channels (stdout, file, webhook)."""
from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass
from typing import List, Optional

from stackdiff.alerter import Alert


@dataclass
class NotifyResult:
    channel: str
    success: bool
    message: str

    def as_dict(self) -> dict:
        return {"channel": self.channel, "success": self.success, "message": self.message}


def notify_stdout(alerts: List[Alert]) -> NotifyResult:
    """Print alerts to stdout."""
    if not alerts:
        print("[notifier] No alerts to report.")
        return NotifyResult("stdout", True, "no alerts")
    for alert in alerts:
        print(f"[{alert.level.upper()}] {alert.rule}: {alert.message}")
    return NotifyResult("stdout", True, f"{len(alerts)} alert(s) printed")


def notify_file(alerts: List[Alert], path: str) -> NotifyResult:
    """Write alerts as JSON to a file."""
    try:
        payload = [a.as_dict() for a in alerts]
        with open(path, "w") as fh:
            json.dump(payload, fh, indent=2)
        return NotifyResult("file", True, f"wrote {len(alerts)} alert(s) to {path}")
    except OSError as exc:
        return NotifyResult("file", False, str(exc))


def notify_webhook(alerts: List[Alert], url: str, timeout: int = 5) -> NotifyResult:
    """POST alerts as JSON to a webhook URL."""
    payload = json.dumps([a.as_dict() for a in alerts]).encode()
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = resp.status
        return NotifyResult("webhook", True, f"HTTP {status}")
    except Exception as exc:  # noqa: BLE001
        return NotifyResult("webhook", False, str(exc))


def dispatch(
    alerts: List[Alert],
    *,
    stdout: bool = True,
    file_path: Optional[str] = None,
    webhook_url: Optional[str] = None,
) -> List[NotifyResult]:
    """Dispatch alerts to all configured channels."""
    results: List[NotifyResult] = []
    if stdout:
        results.append(notify_stdout(alerts))
    if file_path:
        results.append(notify_file(alerts, file_path))
    if webhook_url:
        results.append(notify_webhook(alerts, webhook_url))
    return results
