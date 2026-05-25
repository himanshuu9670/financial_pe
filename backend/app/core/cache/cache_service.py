"""Backward-compatible facade — delegates to app.cache."""

from __future__ import annotations

from typing import Any

from app.cache import extraction_cache, invalidate_statement
from app.cache.metrics import snapshot as cache_snapshot
from app.core.config import get_settings
from app.core.database.redis_client import get_redis as _get_redis


def get_redis():
    """Backward-compatible accessor for tests expecting `get_redis` in this module."""
    return _get_redis()



class CacheService:
    """Legacy API used by Phase 10 services — maps to modular cache layer."""

    PREFIX = "sf:v1"

    def _enabled(self) -> bool:
        return get_settings().redis_cache_enabled

    def get_extraction(self, statement_id: str, pages: str = "all") -> dict | list | None:
        # Prefer direct redis access when available so legacy callers/tests can patch get_redis
        if self._enabled():
            import json
            from app.cache.cache_keys import statement_extraction_key

            key = statement_extraction_key(statement_id, pages)
            try:
                raw = get_redis().get(key)
                if not raw:
                    return None
                return json.loads(raw)
            except Exception:
                # Fallback to modular extraction cache on error
                return extraction_cache.get_statement_extraction(statement_id, pages)
        return extraction_cache.get_statement_extraction(statement_id, pages)

    def set_extraction(self, statement_id: str, data: dict, pages: str = "all") -> None:
        # Prefer direct redis access when available so legacy callers/tests can patch get_redis
        if self._enabled():
            import json
            from app.cache.cache_keys import statement_extraction_key

            key = statement_extraction_key(statement_id, pages)
            try:
                ttl = get_settings().cache_ttl_extraction
                get_redis().setex(key, ttl, json.dumps(data, default=str))
                return
            except Exception:
                # Fall through to modular extraction cache on error
                pass
        extraction_cache.set_statement_extraction(statement_id, data, pages)

    def get_ai_report(self, statement_id: str) -> dict | None:
        return extraction_cache.get_ai(statement_id)

    def set_ai_report(self, statement_id: str, data: dict) -> None:
        extraction_cache.set_ai(statement_id, data)

    def delete_pattern(self, statement_id: str) -> int:
        return invalidate_statement(statement_id)

    @staticmethod
    def fingerprint_payload(payload: str) -> str:
        import hashlib

        return hashlib.sha256(payload.encode()).hexdigest()[:16]


cache_service = CacheService()

__all__ = ["CacheService", "cache_service", "cache_snapshot"]
