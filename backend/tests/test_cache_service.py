"""Cache service unit tests (mocked Redis)."""

from unittest.mock import MagicMock, patch

from app.core.cache.cache_service import CacheService


@patch("app.core.cache.cache_service.get_settings")
@patch("app.core.cache.cache_service.get_redis")
def test_cache_set_get_json(mock_redis_fn, mock_settings):
    mock_settings.return_value.redis_cache_enabled = True
    store = {}
    r = MagicMock()

    def setex(key, ttl, val):
        store[key] = val

    def get(key):
        return store.get(key)

    r.setex = setex
    r.get = get
    r.delete = lambda k: store.pop(k, None)
    r.scan_iter = lambda *a, **k: []
    mock_redis_fn.return_value = r

    svc = CacheService()
    svc.set_extraction("stmt-1", {"total_pages": 1}, "all")
    out = svc.get_extraction("stmt-1", "all")
    assert out == {"total_pages": 1}
