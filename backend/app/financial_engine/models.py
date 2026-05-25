"""Financial ledger and edit-session domain models."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from app.shared.models import StructuredTransaction, TransactionCoordinates, TransactionSummary


class ChangeType(str, Enum):
    DEBIT = "debit"
    CREDIT = "credit"
    BALANCE = "balance"
    DESCRIPTION = "description"
    DATE = "date"
    INSERT = "insert"
    DELETE = "delete"


class LedgerEntry(BaseModel):
    """Single row in the ordered transaction ledger."""

    transaction_id: str
    row_index: int
    page: int
    date: str | None = None
    description: str = ""
    debit: Decimal | None = None
    credit: Decimal | None = None
    balance: Decimal | None = None
    previous_balance: Decimal | None = None

    coordinates: TransactionCoordinates = Field(default_factory=TransactionCoordinates)
    row_bbox: list[float] = Field(default_factory=list)
    font_metadata: dict[str, Any] = Field(default_factory=dict)

    original_debit: Decimal | None = None
    original_credit: Decimal | None = None
    original_balance: Decimal | None = None

    is_modified: bool = False
    propagation_affected: bool = False
    validation_warnings: list[str] = Field(default_factory=list)

    @classmethod
    def from_structured(cls, txn: StructuredTransaction) -> LedgerEntry:
        return cls(
            transaction_id=txn.transaction_id,
            row_index=txn.row_index,
            page=txn.page,
            date=txn.date,
            description=txn.description,
            debit=txn.debit,
            credit=txn.credit,
            balance=txn.balance,
            coordinates=txn.coordinates,
            row_bbox=txn.row_bbox,
            font_metadata=txn.font_metadata.model_dump(),
            original_debit=txn.debit,
            original_credit=txn.credit,
            original_balance=txn.balance,
        )

    def to_structured(self) -> StructuredTransaction:
        from app.shared.models import FontMetadata

        return StructuredTransaction(
            transaction_id=self.transaction_id,
            page=self.page,
            row_index=self.row_index,
            date=self.date,
            description=self.description,
            debit=self.debit,
            credit=self.credit,
            balance=self.balance,
            coordinates=self.coordinates,
            font_metadata=FontMetadata.model_validate(self.font_metadata),
            row_bbox=self.row_bbox,
            validation_warnings=self.validation_warnings,
        )


class TransactionNode(BaseModel):
    """Node in the dependency graph."""

    transaction_id: str
    index: int
    previous_id: str | None = None
    next_id: str | None = None
    depends_on_balance: bool = True


class DependencyGraph(BaseModel):
    nodes: list[TransactionNode] = Field(default_factory=list)
    opening_balance: Decimal | None = None

    def ordered_ids(self) -> list[str]:
        return [n.transaction_id for n in sorted(self.nodes, key=lambda x: x.index)]


class TransactionPatch(BaseModel):
    transaction_id: str
    field: ChangeType
    old_value: str | None = None
    new_value: str | None = None


class EditOperation(BaseModel):
    operation_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    patches: list[TransactionPatch] = Field(default_factory=list)
    description: str = ""
    inverse_patches: list[TransactionPatch] = Field(default_factory=list)


class PropagationTrace(BaseModel):
    transaction_id: str
    field: str
    old_value: str | None
    new_value: str | None
    reason: str = "downstream_propagation"


class AuditRecord(BaseModel):
    operation_id: str
    action: str
    patches: list[TransactionPatch] = Field(default_factory=list)
    propagation_traces: list[PropagationTrace] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EditSessionState(BaseModel):
    session_id: str
    statement_id: str
    bank: str = "UNKNOWN"
    entries: list[LedgerEntry] = Field(default_factory=list)
    graph: DependencyGraph = Field(default_factory=DependencyGraph)
    summary: TransactionSummary = Field(default_factory=TransactionSummary)
    opening_balance: Decimal | None = None
    validation_passed: bool = True
    validation_issues: list[str] = Field(default_factory=list)
    modified_count: int = 0
    can_undo: bool = False
    can_redo: bool = False
    propagation_trace: list[PropagationTrace] = Field(default_factory=list)
    edit_timeline: list[dict[str, Any]] = Field(default_factory=list)
