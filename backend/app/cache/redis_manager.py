"""Redis connection wrapper with JSON helpers and latency tracking."""

from __future__ import annotations

import json
import time
from typing import Any

from app.core.config import get_settings
from app.core.database.redis_client import get_redis
from app.utils.logging import get_logger

logger = get_logger(__name__)


class RedisManager:
    def enabled(self) -> bool:
        return get_settings().redis_cache_enabled

    def get_raw(self, key: str) -> str | None:
        if not self.enabled():
            return None
        start = time.perf_counter()
        try:
            val = get_redis().get(key)
            latency_ms = (time.perf_counter() - start) * 1000
            from app.cache.metrics import record_latency, record_op

            record_latency(latency_ms)
            if val is not None:
                record_op("redis", "hit")
            else:
                record_op("redis", "miss")
            return val
        except Exception as exc:
            logger.warning("redis_get_failed", key=key, error=str(exc))
            from app.cache.metrics import record_op

            record_op("redis", "error")
            return None

    def get_json(self, key: str) -> dict | list | None:
        raw = self.get_raw(key)
        if not raw:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("redis_json_decode_failed", key=key)
            return None

    def set_json(self, key: str, value: Any, ttl: int) -> bool:
        if not self.enabled():
            return False
        start = time.perf_counter()
        try:
            get_redis().setex(key, ttl, json.dumps(value, default=str))
            from app.cache.metrics import record_latency, record_op

            record_latency((time.perf_counter() - start) * 1000)
            record_op("redis", "set")
            return True
        except Exception as exc:
            logger.warning("redis_set_failed", key=key, error=str(exc))
            return False

    def delete(self, key: str) -> int:
        if not self.enabled():
            return 0
        try:
            return int(get_redis().delete(key))
        except Exception as exc:
            logger.warning("redis_delete_failed", key=key, error=str(exc))
            return 0

    def delete_many(self, keys: list[str]) -> int:
        if not self.enabled() or not keys:
            return 0
        try:
            return int(get_redis().delete(*keys))
        except Exception as exc:
            logger.warning("redis_delete_many_failed", error=str(exc))
            return 0

    def scan_delete(self, pattern: str, *, count: int = 100) -> int:
        if not self.enabled():
            return 0
        deleted = 0
        try:
            r = get_redis()
            for key in r.scan_iter(pattern, count=count):
                deleted += int(r.delete(key))
        except Exception as exc:
            logger.warning("redis_scan_delete_failed", pattern=pattern, error=str(exc))
        return deleted


redis_manager = RedisManager()
