from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.auth.dependencies import require_role_dep
from app.auth.permissions import Role
from app.cache.metrics import persist_snapshot, snapshot
from app.core.database import ping_redis
from app.models import AuditLog, ExportJob, Statement, User
from app.monitoring.export_metrics import set_queue_depth
from app.monitoring.health import run_health_checks
from app.monitoring.redis_metrics import aggregate_hit_ratio, cache_overview
from app.monitoring.worker_metrics import inspect_workers
from app.qa.smoke import qa_summary
from app.schemas.admin import (
    AdminStatsResponse,
    AuditLogSchema,
    CacheStatsResponse,
    MonitoringOverviewResponse,
    QaDashboardResponse,
)
router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats", response_model=AdminStatsResponse)
def admin_stats(
    db: Session = Depends(get_db_session),
    _user: User = Depends(require_role_dep(Role.ADMIN)),
) -> AdminStatsResponse:
    since = datetime.now(timezone.utc) - timedelta(hours=24)
    return AdminStatsResponse(
        users=db.scalar(select(func.count()).select_from(User)) or 0,
        statements=db.scalar(select(func.count()).select_from(Statement)) or 0,
        exports_queued=db.scalar(
            select(func.count()).select_from(ExportJob).where(ExportJob.status == "queued")
        )
        or 0,
        exports_failed=db.scalar(
            select(func.count()).select_from(ExportJob).where(ExportJob.status == "failed")
        )
        or 0,
        audit_events_24h=db.scalar(
            select(func.count())
            .select_from(AuditLog)
            .where(AuditLog.created_at >= since)
        )
        or 0,
    )


@router.get("/monitoring", response_model=MonitoringOverviewResponse)
def monitoring_overview(
    db: Session = Depends(get_db_session),
    _user: User = Depends(require_role_dep(Role.ADMIN)),
) -> MonitoringOverviewResponse:
    from app.core.config import get_settings

    health = run_health_checks(db)
    workers = inspect_workers()
    cache = cache_overview()
    exports_queued = db.scalar(
        select(func.count()).select_from(ExportJob).where(ExportJob.status == "queued")
    ) or 0
    exports_failed = db.scalar(
        select(func.count()).select_from(ExportJob).where(ExportJob.status == "failed")
    ) or 0
    queue_depth = exports_queued + (
        db.scalar(
            select(func.count()).select_from(ExportJob).where(ExportJob.status == "processing")
        )
        or 0
    )
    set_queue_depth(queue_depth)

    return MonitoringOverviewResponse(
        status=health["status"],
        health=health,
        workers=workers,
        cache={
            **cache,
            "aggregate_hit_ratio": aggregate_hit_ratio(),
            "enabled": get_settings().redis_cache_enabled,
        },
        exports={
            "queued": exports_queued,
            "failed": exports_failed,
            "queue_depth": queue_depth,
        },
        timestamp=datetime.now(timezone.utc),
    )


@router.get("/cache-stats", response_model=CacheStatsResponse)
def cache_stats(
    _user: User = Depends(require_role_dep(Role.ADMIN)),
) -> CacheStatsResponse:
    from app.core.config import get_settings

    persist_snapshot()
    return CacheStatsResponse(
        redis_connected=ping_redis(),
        cache_enabled=get_settings().redis_cache_enabled,
        stats=snapshot(),
    )


@router.get("/qa-dashboard", response_model=QaDashboardResponse)
def qa_dashboard(
    db: Session = Depends(get_db_session),
    _user: User = Depends(require_role_dep(Role.ADMIN)),
) -> QaDashboardResponse:
    """Phase 11 — internal QA reliability dashboard."""
    from app.core.config import get_settings

    from app.workers.resilience import celery_resilience_overview

    summary = qa_summary()
    health = run_health_checks(db)
    cache = cache_overview()
    celery_stats = celery_resilience_overview(db)
    exports_queued = celery_stats["exports"]["queued"]
    exports_failed = celery_stats["exports"]["failed"]

    overall = summary["status"]
    if celery_stats["recovery_status"] == "unhealthy":
        overall = "unhealthy"
    elif celery_stats["recovery_status"] == "degraded" and overall == "healthy":
        overall = "degraded"

    return QaDashboardResponse(
        status=overall,
        checks=summary["checks"],
        failed_count=summary["failed_count"] + celery_stats["dead_letters_24h"],
        warn_count=summary["warn_count"] + celery_stats["retries_24h"],
        health=health,
        cache={**cache, "enabled": get_settings().redis_cache_enabled},
        exports={
            "queued": exports_queued,
            "failed": exports_failed,
            "processing": celery_stats["exports"]["processing"],
        },
        celery=celery_stats,
        generated_at=datetime.now(timezone.utc),
    )


@router.get("/audit-logs", response_model=list[AuditLogSchema])
def audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db_session),
    _user: User = Depends(require_role_dep(Role.ADMIN)),
) -> list[AuditLogSchema]:
    q = select(AuditLog).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit)
    return [AuditLogSchema.model_validate(r) for r in db.scalars(q).all()]
