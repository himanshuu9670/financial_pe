"""Comprehensive health checks — read-only, no engine changes."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import ping_redis
from app.monitoring.redis_metrics import collect_redis_info
from app.monitoring.worker_metrics import inspect_workers
from app.services.storage_optimizer import StorageOptimizer


def check_database(db: Session) -> bool:
    try:
        db.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def check_ocr_engine() -> dict:
    try:
        from app.ocr_engine.ocr_processor import TesseractOcrProcessor

        proc = TesseractOcrProcessor()
        return {"available": proc.is_available(), "engine": "tesseract"}
    except Exception as exc:
        return {"available": False, "error": str(exc)[:200]}


def check_storage() -> dict:
    settings = get_settings()
    try:
        settings.ensure_storage_dirs()
        root = Path(settings.storage_root)
        writable = root.exists() and root.is_dir()
        usage = StorageOptimizer().disk_usage_summary()
        return {"writable": writable, "usage_bytes": usage}
    except Exception as exc:
        return {"writable": False, "error": str(exc)[:200]}


def run_health_checks(db: Session | None = None) -> dict:
    settings = get_settings()
    db_ok = check_database(db) if db is not None else False
    redis_info = collect_redis_info()
    redis_ok = redis_info.get("connected", False)
    workers = inspect_workers()
    ocr = check_ocr_engine()
    storage = check_storage()

    checks = {
        "database": db_ok,
        "redis": redis_ok,
        "celery": workers.get("workers_online", 0) > 0,
        "ocr": ocr.get("available", False),
        "storage": storage.get("writable", False),
    }
    healthy_count = sum(1 for v in checks.values() if v)
    if healthy_count == len(checks):
        status = "healthy"
    elif db_ok and redis_ok:
        status = "degraded"
    else:
        status = "unhealthy"

    return {
        "status": status,
        "app": settings.app_name,
        "env": settings.app_env,
        "checks": checks,
        "redis": redis_info,
        "celery": workers,
        "ocr": ocr,
        "storage": storage,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
