"""Backward-compatible re-exports — canonical metrics live in app.monitoring.metrics."""

from __future__ import annotations

import time

from app.monitoring.api_metrics import record_request
from app.monitoring.metrics import (
    AI_JOBS,
    CACHE_OPS,
    CONTENT_TYPE_LATEST,
    EXPORT_JOBS,
    OCR_JOBS,
    PDF_EXTRACTION,
    REQUEST_COUNT,
    REQUEST_LATENCY,
    Timer,
    prometheus_response,
    setup_metrics,
)


__all__ = [
    "AI_JOBS",
    "CACHE_OPS",
    "CONTENT_TYPE_LATEST",
    "EXPORT_JOBS",
    "OCR_JOBS",
    "PDF_EXTRACTION",
    "REQUEST_COUNT",
    "REQUEST_LATENCY",
    "Timer",
    "prometheus_response",
    "record_request",
    "setup_metrics",
]
