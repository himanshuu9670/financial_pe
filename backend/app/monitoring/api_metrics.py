"""HTTP API performance metrics."""

from __future__ import annotations

from app.monitoring.metrics import (
    REQUEST_COUNT,
    REQUEST_LATENCY,
    SLOW_REQUESTS,
    SLOW_REQUEST_THRESHOLD_SEC,
    UPLOAD_LATENCY,
)


def record_request(method: str, endpoint: str, status: int, duration: float) -> None:
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=str(status)).inc()
    REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)
    if duration >= SLOW_REQUEST_THRESHOLD_SEC:
        SLOW_REQUESTS.labels(method=method, endpoint=endpoint).inc()
    if "/upload" in endpoint and method == "POST":
        UPLOAD_LATENCY.observe(duration)


def record_upload(duration: float) -> None:
    UPLOAD_LATENCY.observe(duration)
