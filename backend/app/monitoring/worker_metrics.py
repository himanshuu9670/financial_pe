"""Celery worker and queue observability."""

from __future__ import annotations

import time

from app.monitoring.metrics import CELERY_ACTIVE_TASKS, CELERY_TASK_RETRIES

_worker_start = time.time()


def record_retry(task_name: str) -> None:
    CELERY_TASK_RETRIES.labels(task=task_name).inc()


def inspect_workers(timeout: float = 1.0) -> dict:
    """Non-blocking Celery inspect snapshot."""
    out: dict = {
        "workers_online": 0,
        "active_tasks": 0,
        "reserved_tasks": 0,
        "queues": {},
        "uptime_seconds": int(time.time() - _worker_start),
    }
    try:
        from app.workers.celery_app import celery_app

        insp = celery_app.control.inspect(timeout=timeout)
        if not insp:
            return out
        ping = insp.ping() or {}
        out["workers_online"] = len(ping)
        active = insp.active() or {}
        reserved = insp.reserved() or {}
        active_count = sum(len(v) for v in active.values())
        reserved_count = sum(len(v) for v in reserved.values())
        out["active_tasks"] = active_count
        out["reserved_tasks"] = reserved_count
        CELERY_ACTIVE_TASKS.set(active_count + reserved_count)
        for worker, tasks in active.items():
            for t in tasks:
                q = t.get("delivery_info", {}).get("routing_key", "default")
                out["queues"][q] = out["queues"].get(q, 0) + 1
    except Exception as exc:
        out["error"] = str(exc)[:200]
    return out
