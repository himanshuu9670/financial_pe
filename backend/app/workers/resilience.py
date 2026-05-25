"""Celery retry logging, dead-letter handling, and idempotency guards."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import AuditLog, ExportJob, Statement
from app.utils.logging import get_logger

logger = get_logger(__name__)

ACTION_RETRY = "async.retry"
ACTION_DEAD_LETTER = "async.dead_letter"
ACTION_RECOVERY = "async.recovery"


def log_retry(
    task_name: str,
    *,
    attempt: int,
    max_retries: int,
    reason: str,
    resource_id: str | None = None,
    statement_id: uuid.UUID | None = None,
) -> None:
    from app.monitoring.worker_metrics import record_retry

    record_retry(task_name)
    logger.warning(
        "celery_task_retry",
        task=task_name,
        attempt=attempt,
        max_retries=max_retries,
        reason=reason[:500],
        resource_id=resource_id,
    )
    try:
        from app.monitoring.metrics import CELERY_RETRY_EVENTS

        CELERY_RETRY_EVENTS.labels(task=task_name, outcome="scheduled").inc()
    except Exception:
        pass


def log_recovery(task_name: str, resource_id: str, *, statement_id: uuid.UUID | None = None) -> None:
    logger.info("celery_task_recovered", task=task_name, resource_id=resource_id)
    try:
        from app.monitoring.metrics import CELERY_RETRY_EVENTS

        CELERY_RETRY_EVENTS.labels(task=task_name, outcome="recovered").inc()
    except Exception:
        pass


def record_dead_letter(
    db: Session,
    *,
    task_name: str,
    resource_id: str,
    error: str,
    statement_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
    details: dict[str, Any] | None = None,
) -> None:
    """Persist dead-letter event — job isolated, safe user-facing failure."""
    from app.audit.audit_service import AuditService
    from app.monitoring.metrics import CELERY_DEAD_LETTERS

    payload = {
        "task": task_name,
        "resource_id": resource_id,
        "error": error[:500],
        **(details or {}),
    }
    AuditService(db).log(
        ACTION_DEAD_LETTER,
        user_id=user_id,
        statement_id=statement_id,
        resource_type="async_task",
        resource_id=resource_id,
        status="failure",
        message=f"{task_name} permanently failed",
        details=payload,
    )
    CELERY_DEAD_LETTERS.labels(task=task_name).inc()
    logger.error(
        "celery_dead_letter",
        task=task_name,
        resource_id=resource_id,
        error=error[:300],
    )


def bump_export_retry_metadata(job: ExportJob, reason: str) -> int:
    meta = dict(job.metadata_json or {})
    count = int(meta.get("retry_count", 0)) + 1
    meta["retry_count"] = count
    meta["last_retry_reason"] = reason[:500]
    meta["last_retry_at"] = datetime.now(timezone.utc).isoformat()
    job.metadata_json = meta
    return count


def mark_export_dead_letter(job: ExportJob, error: str) -> None:
    meta = dict(job.metadata_json or {})
    meta["dead_letter"] = True
    meta["dead_letter_at"] = datetime.now(timezone.utc).isoformat()
    meta["user_message"] = (
        "Export could not be completed. Your statement edits are safe; please try exporting again."
    )
    job.metadata_json = meta
    job.error_message = error[:2000]


def mark_statement_processing_error(stmt: Statement, error: str) -> None:
    stmt.status = "error"
    stmt.processing_error = error[:2000]
    meta = dict(stmt.metadata_json or {})
    meta["async_dead_letter"] = True
    meta["user_message"] = (
        "We could not finish processing this PDF. Please re-upload or contact support."
    )
    stmt.metadata_json = meta


def export_job_idempotent_skip(job: ExportJob) -> dict | None:
    """Skip work if export already completed (retry / duplicate delivery)."""
    if job.status == "completed":
        return {
            "job_id": str(job.id),
            "status": "completed",
            "idempotent": True,
            "path": job.output_path,
        }
    if job.status == "failed" and (job.metadata_json or {}).get("dead_letter"):
        return {
            "job_id": str(job.id),
            "status": "failed",
            "dead_letter": True,
            "error": job.error_message,
            "user_message": (job.metadata_json or {}).get("user_message"),
        }
    return None


def celery_resilience_overview(db: Session) -> dict:
    """Aggregate retry/dead-letter/queue metrics for admin QA."""
    from datetime import timedelta

    since = datetime.now(timezone.utc) - timedelta(hours=24)
    retries_24h = (
        db.scalar(
            select(func.count())
            .select_from(AuditLog)
            .where(AuditLog.action == ACTION_RETRY, AuditLog.created_at >= since)
        )
        or 0
    )
    dead_letters_24h = (
        db.scalar(
            select(func.count())
            .select_from(AuditLog)
            .where(AuditLog.action == ACTION_DEAD_LETTER, AuditLog.created_at >= since)
        )
        or 0
    )
    recoveries_24h = (
        db.scalar(
            select(func.count())
            .select_from(AuditLog)
            .where(AuditLog.action == ACTION_RECOVERY, AuditLog.created_at >= since)
        )
        or 0
    )
    exports_queued = (
        db.scalar(
            select(func.count()).select_from(ExportJob).where(ExportJob.status == "queued")
        )
        or 0
    )
    exports_processing = (
        db.scalar(
            select(func.count()).select_from(ExportJob).where(ExportJob.status == "processing")
        )
        or 0
    )
    exports_failed = (
        db.scalar(
            select(func.count()).select_from(ExportJob).where(ExportJob.status == "failed")
        )
        or 0
    )
    statements_error = (
        db.scalar(select(func.count()).select_from(Statement).where(Statement.status == "error"))
        or 0
    )

    from app.monitoring.worker_metrics import inspect_workers

    workers = inspect_workers()
    backlog = exports_queued + exports_processing + workers.get("reserved_tasks", 0)

    recovery_status = "healthy"
    if dead_letters_24h > 10 or workers.get("workers_online", 0) == 0:
        recovery_status = "degraded"
    if dead_letters_24h > 50:
        recovery_status = "unhealthy"

    return {
        "recovery_status": recovery_status,
        "retries_24h": retries_24h,
        "dead_letters_24h": dead_letters_24h,
        "recoveries_24h": recoveries_24h,
        "queue_backlog": backlog,
        "exports": {
            "queued": exports_queued,
            "processing": exports_processing,
            "failed": exports_failed,
        },
        "statements_error": statements_error,
        "workers": workers,
    }
