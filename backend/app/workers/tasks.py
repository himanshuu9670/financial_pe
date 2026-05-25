import uuid

from app.monitoring.metrics import AI_JOBS, EXPORT_JOBS, OCR_JOBS
from app.utils.logging import get_logger
from app.workers.celery_app import celery_app
from app.core.database import SessionLocal
from app.workers.resilience import (
    ACTION_RECOVERY,
    ACTION_RETRY,
    bump_export_retry_metadata,
    export_job_idempotent_skip,
    log_retry,
    mark_export_dead_letter,
    mark_statement_processing_error,
    record_dead_letter,
)
from app.workers.task_impl import execute_pdf_export, execute_statement_pdf_processing

logger = get_logger(__name__)


def _audit_retry(
    db,
    *,
    task_name: str,
    resource_id: str,
    attempt: int,
    reason: str,
    statement_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
) -> None:
    from app.audit import AuditService

    AuditService(db).log(
        ACTION_RETRY,
        user_id=user_id,
        statement_id=statement_id,
        resource_type="async_task",
        resource_id=resource_id,
        status="retry",
        message=f"{task_name} retry {attempt}",
        details={"task": task_name, "attempt": attempt, "reason": reason[:500]},
    )


def _run_statement_pdf_task(self, statement_id: str, *, task_label: str) -> dict:
    from app.models import Statement

    attempt = self.request.retries + 1
    logger.info(
        "statement_pdf_task_started",
        task=task_label,
        statement_id=statement_id,
        attempt=attempt,
        max_retries=self.max_retries,
    )
    db = SessionLocal()
    try:
        payload = execute_statement_pdf_processing(statement_id)
        if payload.get("status") == "not_found":
            return payload

        sid = uuid.UUID(statement_id)
        from app.audit import AuditService

        if attempt > 1:
            AuditService(db).log(
                ACTION_RECOVERY,
                statement_id=sid,
                resource_type="async_task",
                resource_id=statement_id,
                status="success",
                message=f"{task_label} recovered after retry",
                details={"task": task_label, "attempt": attempt},
            )
            db.commit()
        OCR_JOBS.labels(status="success").inc()
        return payload
    except Exception as exc:
        OCR_JOBS.labels(status="failure").inc()
        logger.error(
            "statement_pdf_task_failed",
            task=task_label,
            statement_id=statement_id,
            attempt=attempt,
            error=str(exc),
        )
        if self.request.retries < self.max_retries:
            log_retry(
                task_label,
                attempt=attempt,
                max_retries=self.max_retries,
                reason=str(exc),
                resource_id=statement_id,
                statement_id=uuid.UUID(statement_id),
            )
            _audit_retry(
                db,
                task_name=task_label,
                resource_id=statement_id,
                attempt=attempt,
                reason=str(exc),
                statement_id=uuid.UUID(statement_id),
            )
            db.commit()
            raise self.retry(exc=exc, countdown=30)
        sid = uuid.UUID(statement_id)
        stmt = db.get(Statement, sid)
        if stmt:
            mark_statement_processing_error(stmt, str(exc))
            record_dead_letter(
                db,
                task_name=task_label,
                resource_id=statement_id,
                error=str(exc),
                statement_id=sid,
                user_id=stmt.user_id,
            )
            db.commit()
        raise exc
    finally:
        db.close()


@celery_app.task(name="app.workers.tasks.process_statement_pdf", bind=True, max_retries=2)
def process_statement_pdf(self, statement_id: str) -> dict:
    """Async coordinate extraction + transaction parsing."""
    return _run_statement_pdf_task(self, statement_id, task_label="process_statement_pdf")


@celery_app.task(name="app.workers.tasks.run_pdf_export", bind=True, max_retries=2)
def run_pdf_export(self, job_id: str) -> dict:
    """Background invisible PDF export with retry + idempotency."""
    from app.audit import AuditService
    from app.models import ExportJob
    from app.services.export_job_service import ExportJobService

    attempt = self.request.retries + 1
    db = SessionLocal()
    try:
        job = db.get(ExportJob, uuid.UUID(job_id))
        if not job:
            return {"error": "job not found"}

        skipped = export_job_idempotent_skip(job)
        if skipped:
            logger.info("run_pdf_export_idempotent_skip", job_id=job_id, status=skipped["status"])
            return skipped

        if job.status == "queued":
            job.status = "processing"
            db.commit()

        result = execute_pdf_export(job_id)

        if attempt > 1 and result.get("status") == "completed":
            AuditService(db).log(
                ACTION_RECOVERY,
                user_id=job.user_id,
                statement_id=job.statement_id,
                resource_type="async_task",
                resource_id=job_id,
                status="success",
                message="Export recovered after retry",
                details={"attempt": attempt},
            )
            db.commit()

        EXPORT_JOBS.labels(status="success").inc()
        return result
    except Exception as exc:
        EXPORT_JOBS.labels(status="failure").inc()
        logger.error("run_pdf_export_failed", job_id=job_id, attempt=attempt, error=str(exc))
        job = db.get(ExportJob, uuid.UUID(job_id))
        if not job:
            return {"job_id": job_id, "status": "failed", "error": str(exc)}

        if self.request.retries < self.max_retries:
            bump_export_retry_metadata(job, str(exc))
            log_retry(
                "run_pdf_export",
                attempt=attempt,
                max_retries=self.max_retries,
                reason=str(exc),
                resource_id=job_id,
                statement_id=job.statement_id,
            )
            _audit_retry(
                db,
                task_name="run_pdf_export",
                resource_id=job_id,
                attempt=attempt,
                reason=str(exc),
                statement_id=job.statement_id,
                user_id=job.user_id,
            )
            job.status = "processing"
            db.commit()
            raise self.retry(exc=exc, countdown=45)

        try:
            mark_export_dead_letter(job, str(exc))
            ExportJobService(db).mark_failed(job, str(exc))
            record_dead_letter(
                db,
                task_name="run_pdf_export",
                resource_id=job_id,
                error=str(exc),
                statement_id=job.statement_id,
                user_id=job.user_id,
                details={"retry_count": (job.metadata_json or {}).get("retry_count", 0)},
            )
            AuditService(db).log(
                "export.failed",
                user_id=job.user_id,
                statement_id=job.statement_id,
                status="failure",
                message=(job.metadata_json or {}).get("user_message", str(exc)[:500]),
                resource_id=job_id,
            )
            db.commit()
        except Exception:
            pass
        return {
            "job_id": job_id,
            "status": "failed",
            "dead_letter": True,
            "user_message": (job.metadata_json or {}).get("user_message") if job else None,
            "error": str(exc),
        }
    finally:
        db.close()


@celery_app.task(name="app.workers.tasks.cleanup_storage")
def cleanup_storage() -> dict:
    from app.services.storage_optimizer import StorageOptimizer

    return StorageOptimizer().cleanup_temp()


@celery_app.task(name="app.workers.tasks.run_ocr_pipeline", bind=True, max_retries=2)
def run_ocr_pipeline(self, statement_id: str) -> dict:
    """Dedicated OCR queue entry — same resilience as process_statement_pdf."""
    return _run_statement_pdf_task(self, statement_id, task_label="run_ocr_pipeline")


@celery_app.task(name="app.workers.tasks.run_ai_intelligence", bind=True, max_retries=2)
def run_ai_intelligence(self, statement_id: str) -> dict:
    """Background AI categorization, anomaly detection, and insights."""
    from app.audit import AuditService
    from app.services.ai_intelligence_service import AiIntelligenceService

    attempt = self.request.retries + 1
    db = SessionLocal()
    try:
        report, cached = AiIntelligenceService(db).analyze(
            uuid.UUID(statement_id),
            force_refresh=True,
        )
        if attempt > 1:
            AuditService(db).log(
                ACTION_RECOVERY,
                statement_id=uuid.UUID(statement_id),
                resource_type="async_task",
                resource_id=statement_id,
                status="success",
                message="AI pipeline recovered after retry",
            )
            db.commit()
        AI_JOBS.labels(status="success").inc()
        return {
            "statement_id": statement_id,
            "status": "completed",
            "cached": cached,
            "confidence": report.confidence.overall,
            "anomalies": len(report.anomalies),
            "categories": len(report.categories),
        }
    except Exception as exc:
        AI_JOBS.labels(status="failure").inc()
        logger.error("run_ai_intelligence_failed", statement_id=statement_id, error=str(exc))
        if self.request.retries < self.max_retries:
            log_retry(
                "run_ai_intelligence",
                attempt=attempt,
                max_retries=self.max_retries,
                reason=str(exc),
                resource_id=statement_id,
                statement_id=uuid.UUID(statement_id),
            )
            _audit_retry(
                db,
                task_name="run_ai_intelligence",
                resource_id=statement_id,
                attempt=attempt,
                reason=str(exc),
                statement_id=uuid.UUID(statement_id),
            )
            db.commit()
            raise self.retry(exc=exc, countdown=20)
        record_dead_letter(
            db,
            task_name="run_ai_intelligence",
            resource_id=statement_id,
            error=str(exc),
            statement_id=uuid.UUID(statement_id),
        )
        db.commit()
        return {
            "statement_id": statement_id,
            "status": "failed",
            "dead_letter": True,
            "user_message": "AI analysis could not be completed. Core statement data remains available.",
            "error": str(exc),
        }
    finally:
        db.close()
