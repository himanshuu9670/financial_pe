import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Statement
from app.pdf_engine import PdfParser
from app.pdf_engine.exceptions import PdfEngineError
from app.services.storage_service import StorageService
from app.utils.logging import get_logger

logger = get_logger(__name__)
DEMO_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


class StatementService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.storage = StorageService()

    def list_statements(self, skip: int = 0, limit: int = 50) -> tuple[list[Statement], int]:
        total = self.db.scalar(select(func.count()).select_from(Statement)) or 0
        query = select(Statement).order_by(Statement.created_at.desc()).offset(skip).limit(limit)
        items = list(self.db.scalars(query).all())
        return items, total

    def get_by_id(self, statement_id: uuid.UUID) -> Statement | None:
        return self.db.get(Statement, statement_id)

    async def create_from_upload(
        self,
        upload: UploadFile,
        user_id: uuid.UUID | None = None,
    ) -> Statement:
        if user_id is None:
            user_id = DEMO_USER_ID

        statement_id = uuid.uuid4()
        original_name = Path(upload.filename or "statement.pdf").name

        if not original_name.lower().endswith(".pdf"):
            raise ValueError("Only PDF files are accepted")

        content_type = (upload.content_type or "").lower()
        if content_type and "pdf" not in content_type and content_type != "application/octet-stream":
            raise ValueError("Invalid content type — PDF required")

        try:
            path_str, pdf_path, file_size = await self.storage.save_original_pdf_async(
                upload, statement_id
            )
            page_count = PdfParser.page_count(pdf_path)
        except PdfEngineError:
            raise
        except Exception as exc:
            logger.error("upload_failed", error=str(exc))
            raise

        statement = Statement(
            id=statement_id,
            user_id=user_id,
            original_filename=original_name,
            original_pdf_path=path_str,
            file_size_bytes=file_size,
            page_count=page_count,
            status="uploaded",
        )
        self.db.add(statement)
        self.db.commit()
        self.db.refresh(statement)

        logger.info(
            "statement_uploaded",
            statement_id=str(statement_id),
            pages=page_count,
            size=file_size,
        )
        return statement

    def get_pdf_path(self, statement: Statement, edited: bool = False) -> Path | None:
        path_str = statement.edited_pdf_path if edited else statement.original_pdf_path
        if not path_str:
            return None
        path = Path(path_str)
        return path if path.exists() else None
