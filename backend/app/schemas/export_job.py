from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class QueueExportRequest(BaseModel):
    statement_id: UUID
    session_id: str | None = None
    export_name: str | None = None


class ExportJobResponse(BaseModel):
    id: UUID
    statement_id: UUID
    status: str
    export_name: str | None = None
    celery_task_id: str | None = None
    output_path: str | None = None
    replacements_applied: int = 0
    validation_passed: bool | None = None
    error_message: str | None = None
    download_url: str | None = None
    created_at: datetime
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class ExportJobListResponse(BaseModel):
    jobs: list[ExportJobResponse]
    total: int
