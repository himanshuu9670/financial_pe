from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.financial_engine.models import ChangeType


class StartSessionRequest(BaseModel):
    statement_id: UUID


class StartSessionResponse(BaseModel):
    session_id: str
    statement_id: UUID
    message: str = "Edit session started"


class UpdateTransactionRequest(BaseModel):
    session_id: str
    transaction_id: str
    field: ChangeType
    value: str | None = None


class SessionActionRequest(BaseModel):
    session_id: str


class CommitSessionRequest(BaseModel):
    session_id: str
    notes: str | None = None


class FieldCoordinateSchema(BaseModel):
    text: str = ""
    x: float = 0
    y: float = 0
    width: float = 0
    height: float = 0
    bbox: list[float] = Field(default_factory=list)
    field_id: str = ""
    font: str = "Unknown"
    font_size: float = 0.0


class TransactionCoordinatesSchema(BaseModel):
    date: FieldCoordinateSchema | None = None
    description: FieldCoordinateSchema | None = None
    debit: FieldCoordinateSchema | None = None
    credit: FieldCoordinateSchema | None = None
    balance: FieldCoordinateSchema | None = None


class LedgerEntrySchema(BaseModel):
    transaction_id: str
    row_index: int
    page: int
    date: str | None = None
    description: str = ""
    debit: Decimal | None = None
    credit: Decimal | None = None
    balance: Decimal | None = None
    previous_balance: Decimal | None = None
    is_modified: bool = False
    propagation_affected: bool = False
    validation_warnings: list[str] = Field(default_factory=list)
    row_bbox: list[float] = Field(default_factory=list)
    coordinates: TransactionCoordinatesSchema | None = None
    font_metadata: dict[str, Any] = Field(default_factory=dict)


class EditTimelineEventSchema(BaseModel):
    operation_id: str
    timestamp: str
    action: str
    description: str
    transaction_id: str | None = None
    field: str | None = None


class SummarySchema(BaseModel):
    total_debit: Decimal
    total_credit: Decimal
    opening_balance: Decimal | None = None
    closing_balance: Decimal | None = None
    transaction_count: int
    validation_passed: bool = True
    validation_issues: list[str] = Field(default_factory=list)


class PropagationTraceSchema(BaseModel):
    transaction_id: str
    field: str
    old_value: str | None
    new_value: str | None
    reason: str


class DependencyNodeSchema(BaseModel):
    transaction_id: str
    index: int
    previous_id: str | None
    next_id: str | None


class SessionStateResponse(BaseModel):
    session_id: str
    statement_id: UUID
    bank: str
    entries: list[LedgerEntrySchema]
    summary: SummarySchema
    validation_passed: bool
    validation_issues: list[str]
    modified_count: int
    can_undo: bool
    can_redo: bool
    propagation_trace: list[PropagationTraceSchema] = Field(default_factory=list)
    dependency_graph: list[DependencyNodeSchema] = Field(default_factory=list)
    edit_timeline: list[EditTimelineEventSchema] = Field(default_factory=list)
    debug: dict[str, Any] | None = None


class UpdateTransactionResponse(BaseModel):
    success: bool
    state: SessionStateResponse
    propagation_trace: list[PropagationTraceSchema] = Field(default_factory=list)
