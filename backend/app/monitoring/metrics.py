"""Central Prometheus metric registry — lightweight, import-safe."""

from __future__ import annotations

import time

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

# --- API (also used by core.observability for backward compat) ---
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0),
)
SLOW_REQUESTS = Counter(
    "http_slow_requests_total",
    "Requests exceeding slow threshold",
    ["method", "endpoint"],
)
UPLOAD_LATENCY = Histogram(
    "http_upload_duration_seconds",
    "PDF upload request duration",
    buckets=(0.1, 0.5, 1, 2, 5, 10, 30, 60),
)

# --- OCR ---
OCR_DURATION = Histogram(
    "ocr_processing_duration_seconds",
    "OCR pipeline duration per invocation",
    buckets=(1, 2, 5, 10, 30, 60, 120, 300),
)
OCR_CACHE_HITS = Counter("ocr_cache_hits_total", "OCR Redis cache hits")
OCR_CACHE_MISSES = Counter("ocr_cache_misses_total", "OCR Redis cache misses")
OCR_FAILURES = Counter("ocr_failures_total", "OCR processing failures", ["reason"])
OCR_PAGES = Counter("ocr_pages_processed_total", "Pages processed via OCR")
OCR_JOBS = Counter("ocr_jobs_total", "OCR Celery pipeline jobs", ["status"])

# --- Export ---
EXPORT_DURATION = Histogram(
    "export_duration_seconds",
    "PDF export job duration",
    buckets=(1, 5, 10, 30, 60, 120, 300),
)
EXPORT_JOBS = Counter("export_jobs_total", "PDF export jobs", ["status"])
EXPORT_VALIDATION_FAILURES = Counter(
    "export_validation_failures_total",
    "Export typography/validation failures",
)
EXPORT_OVERLAY_FAILURES = Counter(
    "export_overlay_failures_total",
    "Export overlay rendering failures",
)
EXPORT_QUEUE_DEPTH = Gauge("export_queue_depth", "Queued + processing export jobs")

# --- Workers / AI ---
AI_JOBS = Counter("ai_jobs_total", "AI intelligence jobs", ["status"])
CELERY_TASK_RETRIES = Counter(
    "celery_task_retries_total",
    "Celery task retries",
    ["task"],
)
CELERY_RETRY_EVENTS = Counter(
    "celery_retry_events_total",
    "Structured retry/recovery events",
    ["task", "outcome"],
)
CELERY_DEAD_LETTERS = Counter(
    "celery_dead_letters_total",
    "Tasks moved to dead-letter after retry exhaustion",
    ["task"],
)
CELERY_ACTIVE_TASKS = Gauge("celery_active_tasks", "Active Celery tasks (estimate)")

# --- PDF extraction ---
PDF_EXTRACTION = Histogram(
    "pdf_extraction_duration_seconds",
    "PDF coordinate extraction duration",
    buckets=(0.5, 1, 2, 5, 10, 30, 60, 120),
)

# --- Redis cache ---
CACHE_OPS = Counter(
    "cache_operations_total",
    "Redis cache operations",
    ["namespace", "result"],
)
REDIS_MEMORY_BYTES = Gauge("redis_memory_used_bytes", "Redis used memory")
REDIS_CONNECTED = Gauge("redis_connected", "Redis connectivity (1=up)")

SLOW_REQUEST_THRESHOLD_SEC = 2.0


class Timer:
    def __init__(self, histogram) -> None:
        self._histogram = histogram
        self._start = 0.0

    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, *args):
        self._histogram.observe(time.perf_counter() - self._start)


def setup_metrics() -> None:
    """Register collectors (import side-effect)."""
    return None


def prometheus_response() -> tuple[bytes, str]:
    return generate_latest(), CONTENT_TYPE_LATEST


def setup_monitoring() -> None:
    """App startup hook — metrics + structured logging."""
    from app.utils.logging import setup_logging

    setup_logging()
    setup_metrics()
