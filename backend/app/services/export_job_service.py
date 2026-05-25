"""Async export queue with status tracking."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ExportJob
from app.services.secure_download import SecureDownloadService
from app.utils.logging import get_logger
from app.workers.tasks import run_pdf_export

logger = get_logger(__name__)


class ExportJobService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.secure = SecureDownloadService()

    def queue_export(
        self,
        statement_id: uuid.UUID,
        user_id: uuid.UUID | None,
        *,
        session_id: str | None = None,
        export_name: str | None = None,
    ) -> ExportJob:

        active = self.db.scalars(
            select(ExportJob)
            .where(
                ExportJob.statement_id == statement_id,
                ExportJob.status.in_(("queued", "processing")),
            )
            .order_by(ExportJob.created_at.desc())
            .limit(1)
        ).first()
        if active:
            logger.info(
                "export_duplicate_prevented",
                statement_id=str(statement_id),
                existing_job=str(active.id),
            )
            return active

        job = ExportJob(
            statement_id=statement_id,
            user_id=user_id,
            status="queued",
            export_name=export_name or f"export_{statement_id}.pdf",
            metadata_json={"session_id": session_id} if session_id else None,
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)

        task = run_pdf_export.delay(str(job.id))
        job.celery_task_id = task.id
        job.status = "processing"
        self.db.commit()
        self.db.refresh(job)

        logger.info("export_queued", job_id=str(job.id), task_id=task.id)
        return job

    def get_job(self, job_id: uuid.UUID) -> ExportJob | None:
        return self.db.get(ExportJob, job_id)

    def list_for_statement(self, statement_id: uuid.UUID) -> list[ExportJob]:
        q = (
            select(ExportJob)
            .where(ExportJob.statement_id == statement_id)
            .order_by(ExportJob.created_at.desc())
        )
        return list(self.db.scalars(q).all())

    def mark_completed(
        self,
        job: ExportJob,
        *,
        output_path: str,
        replacements: int,
        validation_passed: bool,
        snapshot_id: uuid.UUID | None = None,
    ) -> None:
        job.status = "completed"
        job.output_path = output_path
        job.replacements_applied = replacements
        job.validation_passed = validation_passed
        job.snapshot_id = snapshot_id
        job.completed_at = datetime.now(timezone.utc)
        job.download_token_expires_at = datetime.now(timezone.utc) + self.secure.token_ttl_delta()
        self.db.commit()

    def mark_failed(self, job: ExportJob, error: str) -> None:
        job.status = "failed"
        job.error_message = error[:2000]
        job.completed_at = datetime.now(timezone.utc)
        self.db.commit()
