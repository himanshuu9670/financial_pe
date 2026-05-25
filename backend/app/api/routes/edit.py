import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.financial_engine.models import ChangeType, EditSessionState
from app.schemas.edit_session import (
    CommitSessionRequest,
    DependencyNodeSchema,
    EditTimelineEventSchema,
    FieldCoordinateSchema,
    LedgerEntrySchema,
    PropagationTraceSchema,
    SessionActionRequest,
    SessionStateResponse,
    StartSessionRequest,
    StartSessionResponse,
    SummarySchema,
    TransactionCoordinatesSchema,
    UpdateTransactionRequest,
    UpdateTransactionResponse,
)
from app.services.edit_session_service import EditSessionService

router = APIRouter(prefix="/edit", tags=["edit"])


def _coord_schema(coord) -> FieldCoordinateSchema | None:
    if not coord:
        return None
    return FieldCoordinateSchema(
        text=coord.text,
        x=coord.x,
        y=coord.y,
        width=coord.width,
        height=coord.height,
        bbox=coord.bbox,
        font=coord.font,
        font_size=coord.font_size,
    )


def _entry_coordinates(entry) -> TransactionCoordinatesSchema | None:
    c = entry.coordinates
    if not c:
        return None
    return TransactionCoordinatesSchema(
        date=_coord_schema(c.date),
        description=_coord_schema(c.description),
        debit=_coord_schema(c.debit),
        credit=_coord_schema(c.credit),
        balance=_coord_schema(c.balance),
    )


def _state_to_response(state: EditSessionState, *, debug: bool = False) -> SessionStateResponse:
    summary = SummarySchema(
        total_debit=state.summary.total_debit,
        total_credit=state.summary.total_credit,
        opening_balance=state.summary.opening_balance,
        closing_balance=state.summary.closing_balance,
        transaction_count=state.summary.transaction_count,
        validation_passed=state.validation_passed,
        validation_issues=state.validation_issues,
    )
    return SessionStateResponse(
        session_id=state.session_id,
        statement_id=uuid.UUID(state.statement_id),
        bank=state.bank,
        entries=[
            LedgerEntrySchema(
                transaction_id=e.transaction_id,
                row_index=e.row_index,
                page=e.page,
                date=e.date,
                description=e.description,
                debit=e.debit,
                credit=e.credit,
                balance=e.balance,
                previous_balance=e.previous_balance,
                is_modified=e.is_modified,
                propagation_affected=e.propagation_affected,
                validation_warnings=e.validation_warnings,
                row_bbox=e.row_bbox,
                coordinates=_entry_coordinates(e),
                font_metadata=e.font_metadata or {},
            )
            for e in state.entries
        ],
        edit_timeline=[
            EditTimelineEventSchema.model_validate(t) for t in state.edit_timeline
        ],
        summary=summary,
        validation_passed=state.validation_passed,
        validation_issues=state.validation_issues,
        modified_count=state.modified_count,
        can_undo=state.can_undo,
        can_redo=state.can_redo,
        propagation_trace=[
            PropagationTraceSchema(
                transaction_id=t.transaction_id,
                field=t.field,
                old_value=t.old_value,
                new_value=t.new_value,
                reason=t.reason,
            )
            for t in state.propagation_trace
        ],
        dependency_graph=[
            DependencyNodeSchema(
                transaction_id=n.transaction_id,
                index=n.index,
                previous_id=n.previous_id,
                next_id=n.next_id,
            )
            for n in state.graph.nodes
        ],
        debug={
            "opening_balance": str(state.opening_balance) if state.opening_balance else None,
            "audit_entries": len(state.entries),
        }
        if debug
        else None,
    )


@router.post("/start-session", response_model=StartSessionResponse, status_code=status.HTTP_201_CREATED)
def start_edit_session(
    payload: StartSessionRequest,
    db: Session = Depends(get_db_session),
) -> StartSessionResponse:
    service = EditSessionService(db)
    try:
        session_id = service.start_session(payload.statement_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return StartSessionResponse(
        session_id=session_id,
        statement_id=payload.statement_id,
    )


@router.get("/session-state", response_model=SessionStateResponse)
def get_session_state(
    session_id: str = Query(...),
    debug: bool = Query(default=False),
    db: Session = Depends(get_db_session),
) -> SessionStateResponse:
    service = EditSessionService(db)
    try:
        state = service.get_state(session_id, include_debug=debug)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _state_to_response(state, debug=debug)


@router.post("/update-transaction", response_model=UpdateTransactionResponse)
def update_transaction(
    payload: UpdateTransactionRequest,
    db: Session = Depends(get_db_session),
) -> UpdateTransactionResponse:
    service = EditSessionService(db)
    try:
        state = service.update_transaction(
            payload.session_id,
            payload.transaction_id,
            payload.field,
            payload.value,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    response = _state_to_response(state)
    return UpdateTransactionResponse(
        success=True,
        state=response,
        propagation_trace=response.propagation_trace,
    )


@router.post("/undo", response_model=SessionStateResponse)
def undo_edit(
    payload: SessionActionRequest,
    db: Session = Depends(get_db_session),
) -> SessionStateResponse:
    service = EditSessionService(db)
    try:
        state = service.undo(payload.session_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _state_to_response(state)


@router.post("/redo", response_model=SessionStateResponse)
def redo_edit(
    payload: SessionActionRequest,
    db: Session = Depends(get_db_session),
) -> SessionStateResponse:
    service = EditSessionService(db)
    try:
        state = service.redo(payload.session_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _state_to_response(state)


@router.post("/commit", response_model=SessionStateResponse)
def commit_session(
    payload: CommitSessionRequest,
    db: Session = Depends(get_db_session),
) -> SessionStateResponse:
    service = EditSessionService(db)
    try:
        state = service.commit(payload.session_id, payload.notes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _state_to_response(state)
