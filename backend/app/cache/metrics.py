"""Cache hit/miss observability — in-process counters + Redis snapshot."""

from __future__ import annotations

import time
from threading import Lock

from app.cache.redis_manager import redis_manager

_lock = Lock()
_stats: dict[str, dict[str, int]] = {}
_latency_samples: list[float] = []
_MAX_LATENCY_SAMPLES = 200


def record_op(namespace: str, result: str) -> None:
    """result: hit | miss | set | error"""
    with _lock:
        bucket = _stats.setdefault(namespace, {"hit": 0, "miss": 0, "set": 0, "error": 0})
        bucket[result] = bucket.get(result, 0) + 1

    try:
        from app.monitoring.metrics import CACHE_OPS

        CACHE_OPS.labels(namespace=namespace, result=result).inc()
    except Exception:
        pass


def record_latency(ms: float) -> None:
    with _lock:
        _latency_samples.append(ms)
        if len(_latency_samples) > _MAX_LATENCY_SAMPLES:
            _latency_samples.pop(0)


def hit_rate(namespace: str) -> float:
    with _lock:
        b = _stats.get(namespace, {})
        hits = b.get("hit", 0)
        misses = b.get("miss", 0)
        total = hits + misses
        return round(hits / total, 3) if total else 0.0


def snapshot() -> dict:
    with _lock:
        stats_copy = {k: dict(v) for k, v in _stats.items()}
        latencies = list(_latency_samples)

    avg_latency = round(sum(latencies) / len(latencies), 2) if latencies else 0.0
    p95 = 0.0
    if latencies:
        sorted_l = sorted(latencies)
        p95 = round(sorted_l[int(len(sorted_l) * 0.95)], 2)

    return {
        "enabled": redis_manager.enabled(),
        "timestamp": time.time(),
        "namespaces": stats_copy,
        "hit_rates": {ns: hit_rate(ns) for ns in stats_copy},
        "redis_latency_ms": {"avg": avg_latency, "p95": p95},
        "ocr_savings_estimate": stats_copy.get("ocr", {}).get("hit", 0),
        "extraction_savings_estimate": (
            stats_copy.get("extraction", {}).get("hit", 0)
            + stats_copy.get("native", {}).get("hit", 0)
        ),
    }


def persist_snapshot() -> None:
    """Optional periodic persist to Redis for admin dashboard."""
    if not redis_manager.enabled():
        return
    redis_manager.set_json("sf:v2:cache:stats:snapshot", snapshot(), ttl=300)
