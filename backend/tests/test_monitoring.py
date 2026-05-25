"""Monitoring layer smoke tests."""

from unittest.mock import MagicMock, patch

from app.monitoring.health import check_ocr_engine, run_health_checks
from app.monitoring.ocr_metrics import record_cache_hit, record_cache_miss
def test_ocr_metrics_counters():
    record_cache_hit()
    record_cache_miss()


def test_ocr_engine_check():
    result = check_ocr_engine()
    assert "available" in result
    assert "engine" in result


@patch("app.monitoring.health.check_database")
@patch("app.monitoring.health.collect_redis_info")
@patch("app.monitoring.health.inspect_workers")
def test_run_health_checks(mock_workers, mock_redis, mock_db):
    mock_db.return_value = True
    mock_redis.return_value = {"connected": True}
    mock_workers.return_value = {"workers_online": 1}
    report = run_health_checks(MagicMock())
    assert report["status"] in ("healthy", "degraded", "unhealthy")
    assert "checks" in report
