import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.schemas.transaction import TransactionResponseSchema, TransactionsListResponse
from app.services.statement_service import StatementService
from app.services.transaction_service import TransactionService
from app.utils.logging import get_logger

router = APIRouter(tags=["transactions"])
logger = get_logger(__name__)


@router.get("/statements/{statement_id}/transactions", response_model=TransactionsListResponse)
def get_statement_transactions(
    statement_id: uuid.UUID,
    refresh: bool = Query(default=False),
    debug: bool = Query(default=False),
    db: Session = Depends(get_db_session),
) -> TransactionsListResponse:
    stmt_service = StatementService(db)
    statement = stmt_service.get_by_id(statement_id)
    if not statement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Statement not found")

    txn_service = TransactionService(db)

    try:
        result, cached = txn_service.parse_transactions(
            statement_id,
            force_refresh=refresh,
            include_debug=debug,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("transaction_parse_failed", statement_id=str(statement_id), error=str(exc))
        raise HTTPException(status_code=422, detail=f"Transaction parsing failed: {exc}") from exc

    return TransactionsListResponse(
        statement_id=statement_id,
        bank=result.bank,
        bank_confidence=result.bank_confidence,
        transactions=[
            TransactionResponseSchema(
                transaction_id=t.transaction_id,
                page=t.page,
                row_index=t.row_index,
                date=t.date,
                description=t.description,
                debit=t.debit,
                credit=t.credit,
                balance=t.balance,
                coordinates=t.coordinates,
                font_metadata=t.font_metadata.model_dump(),
                row_bbox=t.row_bbox,
                confidence=t.confidence,
                validation_warnings=t.validation_warnings,
            )
            for t in result.transactions
        ],
        summary=result.summary,
        cached=cached,
        warnings=result.warnings,
        debug=result.debug if debug else None,
    )
