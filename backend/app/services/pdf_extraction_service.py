import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import Statement
from app.pdf_engine import PdfParser
from app.pdf_engine.exceptions import PdfEngineError
from app.pdf_engine.models import DocumentExtraction
from app.cache import extraction_cache
from app.monitoring.metrics import PDF_EXTRACTION, Timer
from app.services.statement_service import StatementService
from app.utils.logging import get_logger

logger = get_logger(__name__)


class PdfExtractionService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.statements = StatementService(db)

    def extract(
        self,
        statement_id: uuid.UUID,
        *,
        pages: list[int] | None = None,
        force_refresh: bool = False,
    ) -> tuple[DocumentExtraction, bool]:
        statement = self.statements.get_by_id(statement_id)
        if not statement:
            raise ValueError("Statement not found")

        page_key = "all" if not pages else ",".join(str(p) for p in sorted(pages))
        if not force_refresh and not pages:
            redis_cached = extraction_cache.get_statement_extraction(str(statement_id), page_key)
            if redis_cached:
                return DocumentExtraction.model_validate(redis_cached), True

        if (
            not force_refresh
            and statement.extraction_json
            and statement.status == "ready"
            and not pages
        ):
            cached = DocumentExtraction.model_validate(statement.extraction_json)
            extraction_cache.set_statement_extraction(
                str(statement_id), cached.model_dump(mode="json"), page_key
            )
            return cached, True

        path = self.statements.get_pdf_path(statement)
        if not path:
            raise ValueError("PDF file not found on disk")

        statement.status = "extracting"
        statement.processing_error = None
        self.db.commit()

        try:
            with Timer(PDF_EXTRACTION):
                result = PdfParser.extract(
                    path,
                    statement_id=str(statement_id),
                    pages=pages,
                )
            payload = result.model_dump(mode="json")
            statement.page_count = result.total_pages
            statement.extraction_json = payload
            statement.extracted_at = datetime.now(timezone.utc)
            statement.status = "ready"
            self.db.commit()
            self.db.refresh(statement)
            if not pages:
                extraction_cache.set_statement_extraction(str(statement_id), payload, page_key)
            return result, False
        except PdfEngineError as exc:
            statement.status = "error"
            statement.processing_error = str(exc)
            self.db.commit()
            logger.error("extraction_failed", statement_id=str(statement_id), error=str(exc))
            raise
