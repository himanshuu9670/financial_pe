"""Shared task implementations — keeps Celery bindings thin for retries/idempotency."""

from __future__ import annotations

import uuid
from pathlib import Path

from app.utils.logging import get_logger

logger = get_logger(__name__)


def execute_statement_pdf_processing(statement_id: str) -> dict:
    """Core OCR/extraction pipeline (no Celery retry semantics)."""
    from app.core.database import SessionLocal
    from app.models import Statement
    from app.services.pdf_extraction_service import PdfExtractionService
    from app.services.transaction_service import TransactionService

    db = SessionLocal()
    try:
        sid = uuid.UUID(statement_id)
        stmt = db.get(Statement, sid)
        if not stmt:
            return {"statement_id": statement_id, "status": "not_found"}

        pdf_service = PdfExtractionService(db)
        pdf_service.extract(sid, force_refresh=not stmt.extraction_json)
        txn_service = TransactionService(db)
        result, cached = txn_service.parse_transactions(sid, force_refresh=False)
        if cached:
            logger.info("process_statement_pdf_cache_hit", statement_id=statement_id)
        else:
            result, _ = txn_service.parse_transactions(sid, force_refresh=True)

        stmt = db.get(Statement, sid)
        if stmt and stmt.status == "error":
            stmt.status = "ready"
            stmt.processing_error = None
            db.commit()

        payload = {
            "statement_id": statement_id,
            "status": "ready",
            "transaction_count": len(result.transactions),
            "bank": result.bank,
        }
        from app.core.config import get_settings

        if get_settings().ai_auto_analyze_after_parse and result.transactions:
            from app.workers.celery_app import celery_app

            celery_app.send_task(
                "app.workers.tasks.run_ai_intelligence",
                args=[statement_id],
                queue="ai",
            )
            payload["ai_queued"] = True
        return payload
    finally:
        db.close()


def execute_pdf_export(job_id: str) -> dict:
    """Core export pipeline (no Celery retry semantics)."""
    from app.audit import AuditService
    from app.core.database import SessionLocal
    from app.models import ExportJob
    from app.monitoring.export_metrics import track_export
    from app.monitoring.metrics import EXPORT_VALIDATION_FAILURES
    from app.services.export_job_service import ExportJobService
    from app.services.pdf_export_service import PdfExportService
    from app.services.version_service import VersionService
    from app.workers.resilience import export_job_idempotent_skip

    db = SessionLocal()
    try:
        job = db.get(ExportJob, uuid.UUID(job_id))
        if not job:
            return {"error": "job not found"}

        skipped = export_job_idempotent_skip(job)
        if skipped:
            return skipped

        if job.status == "queued":
            job.status = "processing"
            db.commit()

        export_svc = PdfExportService(db)
        job_svc = ExportJobService(db)
        session_id = (job.metadata_json or {}).get("session_id")

        with track_export():
            result, statement = export_svc.apply_edits(
                job.statement_id,
                session_id=session_id,
            )
        if not result.validation.passed:
            EXPORT_VALIDATION_FAILURES.inc()

        output = Path(result.output_path)
        settings_path = output
        snap = None
        if output.exists():
            version_svc = VersionService(db)
            snap = version_svc.create_snapshot(
                statement,
                output,
                snapshot_type="export",
                user_id=job.user_id,
                metadata={"job_id": job_id, "replacements": result.replacements_applied},
            )
            exports_dir = Path(export_svc.settings.storage_exports) / str(job.statement_id)
            exports_dir.mkdir(parents=True, exist_ok=True)
            export_copy = exports_dir / f"{job.id}.pdf"
            import shutil

            shutil.copy2(output, export_copy)
            settings_path = export_copy

        job_svc.mark_completed(
            job,
            output_path=str(settings_path),
            replacements=result.replacements_applied,
            validation_passed=result.validation.passed,
            snapshot_id=snap.id if snap else None,
        )

        AuditService(db).log(
            "export.completed",
            user_id=job.user_id,
            statement_id=job.statement_id,
            resource_id=job_id,
            details={"replacements": result.replacements_applied},
        )
        db.commit()
        return {"job_id": job_id, "status": "completed", "path": str(settings_path)}
    finally:
        db.close()
