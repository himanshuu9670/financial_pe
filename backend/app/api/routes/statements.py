import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.schemas.statement import StatementListResponse, StatementResponse
from app.services.statement_service import StatementService

router = APIRouter(prefix="/statements", tags=["statements"])


@router.get("", response_model=StatementListResponse)
def list_statements(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db_session),
) -> StatementListResponse:
    service = StatementService(db)
    items, total = service.list_statements(skip=skip, limit=limit)
    return StatementListResponse(
        items=[StatementResponse.model_validate(s) for s in items],
        total=total,
    )


@router.get("/{statement_id}", response_model=StatementResponse)
def get_statement(
    statement_id: uuid.UUID,
    db: Session = Depends(get_db_session),
) -> StatementResponse:
    service = StatementService(db)
    statement = service.get_by_id(statement_id)
    if not statement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Statement not found")
    return StatementResponse.model_validate(statement)
