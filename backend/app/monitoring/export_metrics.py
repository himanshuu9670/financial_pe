"""Export pipeline observability."""

from __future__ import annotations

import time
from contextlib import contextmanager

from app.monitoring.metrics import (
    EXPORT_DURATION,
    EXPORT_OVERLAY_FAILURES,
    EXPORT_QUEUE_DEPTH,
    EXPORT_VALIDATION_FAILURES,
)


def set_queue_depth(depth: int) -> None:
    EXPORT_QUEUE_DEPTH.set(depth)


def record_validation_failure() -> None:
    EXPORT_VALIDATION_FAILURES.inc()


def record_overlay_failure() -> None:
    EXPORT_OVERLAY_FAILURES.inc()


@contextmanager
def track_export():
    start = time.perf_counter()
    try:
        yield
    finally:
        EXPORT_DURATION.observe(time.perf_counter() - start)
