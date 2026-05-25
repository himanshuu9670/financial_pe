from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.ai_engine.models import ParseDebugInfo, TransactionSummary


class FieldCoordinateSchema(BaseModel):
    text: str
    x: float
    y: float
    width: float
    height: float
    bbox: list[float]
    field_id: str
    font: str = "Unknown"
    font_size: float = 0.0


class TransactionCoordinatesSchema(BaseModel):
    date: FieldCoordinateSchema | None = None
    description: FieldCoordinateSchema | None = None
    debit: FieldCoordinateSchema | None = None
    credit: FieldCoordinateSchema | None = None
    balance: FieldCoordinateSchema | None = None


class TransactionResponseSchema(BaseModel):
    transaction_id: str
    page: int
    row_index: int
    date: str | None = None
    description: str = ""
    debit: Decimal | None = None
    credit: Decimal | None = None
    balance: Decimal | None = None
    coordinates: TransactionCoordinatesSchema
    font_metadata: dict[str, Any] = Field(default_factory=dict)
    row_bbox: list[float] = Field(default_factory=list)
    confidence: float = 1.0
    validation_warnings: list[str] = Field(default_factory=list)


class TransactionsListResponse(BaseModel):
    statement_id: UUID
    bank: str
    bank_confidence: float
    transactions: list[TransactionResponseSchema]
    summary: TransactionSummary
    cached: bool = False
    warnings: list[str] = Field(default_factory=list)
    debug: ParseDebugInfo | None = None
    extraction_mode: str = "native"
    layout_confidence: float | None = None
    ocr_confidence: float | None = None
