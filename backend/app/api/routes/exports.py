import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.api.middleware.rate_limit import limiter
from app.core.config import get_settings
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.auth.dependencies import get_current_user, require_role_dep
from app.auth.permissions import Role, can_export
from app.audit import AuditService
from app.models import User
from app.schemas.export_job import ExportJobListResponse, ExportJobResponse, QueueExportRequest
from app.services.export_job_service import ExportJobService
from app.services.secure_download import SecureDownloadService

router = APIRouter(prefix="/exports", tags=["exports"])


def _job_response(job, secure: SecureDownloadService) -> ExportJobResponse:
    download_url = None
    if job.status == "completed" and job.output_path:
        token = secure.create_download_token(
            statement_id=job.statement_id,
            path_kind="export",
            job_id=job.id,
        )
        download_url = f"/api/v1/downloads/secure/{token}"
    return ExportJobResponse(
        id=job.id,
        statement_id=job.statement_id,
        status=job.status,
        export_name=job.export_name,
        celery_task_id=job.celery_task_id,
        output_path=job.output_path,
        replacements_applied=job.replacements_applied,
        validation_passed=job.validation_passed,
        error_message=job.error_message,
        download_url=download_url,
        created_at=job.created_at,
        completed_at=job.completed_at,
    )


@router.post("/queue", response_model=ExportJobResponse, status_code=status.HTTP_202_ACCEPTED)
@limiter.limit(lambda: get_settings().rate_limit_export)
def queue_export(
    request: Request,
    payload: QueueExportRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> ExportJobResponse:
    if not can_export(user.role) and not user.is_superuser:
        raise HTTPException(status_code=403, detail="Export not permitted for viewer role")

    job_svc = ExportJobService(db)
    job = job_svc.queue_export(
        payload.statement_id,
        user.id,
        session_id=payload.session_id,
        export_name=payload.export_name,
    )
    AuditService(db).log(
        "export.queued",
        user_id=user.id,
        statement_id=payload.statement_id,
        resource_id=str(job.id),
    )
    db.commit()
    return _job_response(job, SecureDownloadService())


@router.get("/jobs/{job_id}", response_model=ExportJobResponse)
def get_export_job(
    job_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> ExportJobResponse:
    job = ExportJobService(db).get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Export job not found")
    return _job_response(job, SecureDownloadService())


@router.get("/statement/{statement_id}", response_model=ExportJobListResponse)
def list_statement_exports(
    statement_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> ExportJobListResponse:
    jobs = ExportJobService(db).list_for_statement(statement_id)
    secure = SecureDownloadService()
    return ExportJobListResponse(
        jobs=[_job_response(j, secure) for j in jobs],
        total=len(jobs),
    )
