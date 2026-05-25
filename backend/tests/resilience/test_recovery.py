"""Failure recovery — cache/redis graceful degradation."""

from app.cache.redis_manager import RedisManager
from app.monitoring.health import run_health_checks


def test_redis_manager_disabled_when_cache_off(monkeypatch):
    from app.core.config import get_settings

    settings = get_settings()
    monkeypatch.setattr(settings, "redis_cache_enabled", False)
    mgr = RedisManager()
    assert mgr.enabled() is False
    assert mgr.get_json("missing") is None


def test_health_checks_return_structure():
    health = run_health_checks(db=None)
    assert "status" in health
    assert "checks" in health
