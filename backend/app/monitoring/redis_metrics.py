"""Redis cache and server observability."""

from __future__ import annotations

from app.cache.metrics import snapshot as cache_snapshot
from app.core.database.redis_client import get_redis, ping_redis
from app.monitoring.metrics import REDIS_CONNECTED, REDIS_MEMORY_BYTES


def collect_redis_info() -> dict:
    """Lightweight Redis INFO subset — non-blocking best effort."""
    connected = ping_redis()
    REDIS_CONNECTED.set(1 if connected else 0)
    info: dict = {"connected": connected}
    if not connected:
        return info
    try:
        raw = get_redis().info(section="memory")
        used = raw.get("used_memory", 0)
        REDIS_MEMORY_BYTES.set(used)
        info.update(
            {
                "used_memory_bytes": used,
                "used_memory_human": raw.get("used_memory_human"),
                "maxmemory": raw.get("maxmemory", 0),
                "evicted_keys": raw.get("evicted_keys", 0),
            }
        )
    except Exception as exc:
        info["error"] = str(exc)[:200]
    return info


def cache_overview() -> dict:
    """Merge in-process cache stats with Redis server info."""
    return {
        "cache": cache_snapshot(),
        "redis": collect_redis_info(),
    }


def aggregate_hit_ratio() -> float:
    snap = cache_snapshot()
    rates = snap.get("hit_rates") or {}
    if not rates:
        return 0.0
    return round(sum(rates.values()) / len(rates), 3)
