import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.schemas.common import MessageResponse
from app.services.statement_service import StatementService

router = APIRouter(prefix="/preview", tags=["preview"])


@router.get("/{statement_id}/edited")
def preview_edited_statement(
    statement_id: uuid.UUID,
    db: Session = Depends(get_db_session),
):
    """Serve exported edited PDF."""
    service = StatementService(db)
    statement = service.get_by_id(statement_id)
    if not statement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Statement not found")

    path = service.get_pdf_path(statement, edited=True)
    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Edited PDF not found — run export/apply-edits first",
        )

    return FileResponse(
        path=path,
        media_type="application/pdf",
        filename=f"edited_{statement.original_filename}",
    )


@router.get("/{statement_id}")
def preview_statement(
    statement_id: uuid.UUID,
    db: Session = Depends(get_db_session),
):
    """Serve original PDF for preview."""
    service = StatementService(db)
    statement = service.get_by_id(statement_id)
    if not statement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Statement not found")

    path = service.get_pdf_path(statement, edited=False)
    if not path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PDF file not found")

    return FileResponse(
        path=path,
        media_type="application/pdf",
        filename=statement.original_filename,
    )


@router.get("/{statement_id}/meta", response_model=MessageResponse)
def preview_meta(
    statement_id: uuid.UUID,
    db: Session = Depends(get_db_session),
) -> MessageResponse:
    service = StatementService(db)
    statement = service.get_by_id(statement_id)
    if not statement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Statement not found")
    return MessageResponse(
        message="Preview metadata endpoint ready",
        detail=f"Statement {statement_id} — extraction in Phase 2",
    )
