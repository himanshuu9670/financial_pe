from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMBase


class StatementBase(BaseModel):
    bank_name: str | None = None
    account_number: str | None = None
    status: str = "uploaded"


class StatementCreate(StatementBase):
    original_filename: str
    original_pdf_path: str


class StatementResponse(ORMBase):
    id: UUID
    user_id: UUID
    bank_name: str | None
    account_number: str | None
    original_filename: str
    original_pdf_path: str
    edited_pdf_path: str | None
    preview_path: str | None
    version: int
    status: str
    processing_error: str | None = None
    opening_balance: Decimal | None
    closing_balance: Decimal | None
    page_count: int | None
    file_size_bytes: int | None = None
    extracted_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class StatementListResponse(BaseModel):
    items: list[StatementResponse]
    total: int


class UploadResponse(BaseModel):
    statement_id: UUID
    filename: str
    status: str
    message: str = Field(default="PDF uploaded successfully")
    file_size_bytes: int | None = None
    page_count: int | None = None
    storage_path: str | None = None


class EditRequest(BaseModel):
    """Placeholder for coordinate-based edits — Phase 4+."""

    changes: list[dict] = Field(default_factory=list)


class ExportResponse(BaseModel):
    statement_id: UUID
    download_url: str | None = None
    status: str
    message: str
