import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.pdf_engine.exceptions import PdfEncryptedError, PdfEngineError, PdfValidationError
from app.schemas.extraction import ExtractionResponse
from app.services.pdf_extraction_service import PdfExtractionService
from app.utils.logging import get_logger

router = APIRouter(tags=["extraction"])
logger = get_logger(__name__)


def _parse_pages(pages: str | None) -> list[int] | None:
    if not pages:
        return None
    try:
        return [int(p.strip()) for p in pages.split(",") if p.strip()]
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid pages query format") from exc


@router.get("/statements/{statement_id}/extract", response_model=ExtractionResponse)
def extract_statement(
    statement_id: uuid.UUID,
    pages: str | None = Query(default=None, description="Comma-separated page numbers"),
    refresh: bool = Query(default=False, description="Force re-extraction"),
    db: Session = Depends(get_db_session),
) -> ExtractionResponse:
    service = PdfExtractionService(db)
    page_list = _parse_pages(pages)

    try:
        result, cached = service.extract(
            statement_id,
            pages=page_list,
            force_refresh=refresh or bool(page_list),
        )
    except ValueError as exc:
        if "not found" in str(exc).lower():
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except PdfEncryptedError:
        raise HTTPException(status_code=400, detail="PDF is password-protected")
    except PdfValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except PdfEngineError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    statement = service.statements.get_by_id(statement_id)
    processing_status = statement.status if statement else "unknown"

    return ExtractionResponse(
        **result.model_dump(),
        cached=cached,
        processing_status=processing_status,
    )
