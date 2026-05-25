"""OCR pipeline observability — duration, cache, failures, pages."""

from __future__ import annotations

import time
from contextlib import contextmanager

from app.monitoring.metrics import (
    OCR_CACHE_HITS,
    OCR_CACHE_MISSES,
    OCR_DURATION,
    OCR_FAILURES,
    OCR_PAGES,
)


def record_cache_hit() -> None:
    OCR_CACHE_HITS.inc()


def record_cache_miss() -> None:
    OCR_CACHE_MISSES.inc()


def record_failure(reason: str = "unknown") -> None:
    OCR_FAILURES.labels(reason=reason[:40]).inc()


def record_pages(count: int) -> None:
    if count > 0:
        OCR_PAGES.inc(count)


@contextmanager
def track_ocr_run():
    start = time.perf_counter()
    try:
        yield
    except Exception:
        record_failure("exception")
        raise
    finally:
        OCR_DURATION.observe(time.perf_counter() - start)
