"""diff_profiler.py — timing and performance profiling for stackdiff pipeline runs."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ProfileEntry:
    stage: str
    elapsed_ms: float
    metadata: Dict[str, object] = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "stage": self.stage,
            "elapsed_ms": round(self.elapsed_ms, 3),
            "metadata": self.metadata,
        }


@dataclass
class ProfileReport:
    entries: List[ProfileEntry] = field(default_factory=list)

    @property
    def total_ms(self) -> float:
        return sum(e.elapsed_ms for e in self.entries)

    @property
    def slowest(self) -> Optional[ProfileEntry]:
        return max(self.entries, key=lambda e: e.elapsed_ms) if self.entries else None

    def as_dict(self) -> dict:
        return {
            "total_ms": round(self.total_ms, 3),
            "slowest_stage": self.slowest.stage if self.slowest else None,
            "entries": [e.as_dict() for e in self.entries],
        }


class DiffProfiler:
    """Context-manager-based profiler for named pipeline stages."""

    def __init__(self) -> None:
        self._report = ProfileReport()
        self._stage: Optional[str] = None
        self._start: float = 0.0

    def start_stage(self, stage: str) -> None:
        self._stage = stage
        self._start = time.perf_counter()

    def end_stage(self, metadata: Optional[Dict[str, object]] = None) -> ProfileEntry:
        if self._stage is None:
            raise RuntimeError("end_stage called without a corresponding start_stage")
        elapsed = (time.perf_counter() - self._start) * 1000
        entry = ProfileEntry(
            stage=self._stage,
            elapsed_ms=elapsed,
            metadata=metadata or {},
        )
        self._report.entries.append(entry)
        self._stage = None
        return entry

    @property
    def report(self) -> ProfileReport:
        return self._report


def profile_pipeline(stages: List[str], fn_map: Dict[str, object]) -> ProfileReport:
    """Run each named stage via its callable and return a ProfileReport."""
    profiler = DiffProfiler()
    for stage in stages:
        fn = fn_map.get(stage)
        if fn is None:
            raise KeyError(f"No function registered for stage: {stage!r}")
        profiler.start_stage(stage)
        fn()  # type: ignore[operator]
        profiler.end_stage()
    return profiler.report
