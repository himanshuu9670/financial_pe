from decimal import Decimal
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from app.pdf_engine.models import TextSpan


class FieldCoordinate(BaseModel):
    text: str
    x: float
    y: float
    width: float
    height: float
    bbox: list[float]
    font: str = "Unknown"
    font_size: float = 0.0


class FontMetadata(BaseModel):
    primary_font: str = "Unknown"
    primary_size: float = 0.0
    fields: dict[str, str] = Field(default_factory=dict)


class TransactionCoordinates(BaseModel):
    date: FieldCoordinate | None = None
    description: FieldCoordinate | None = None
    debit: FieldCoordinate | None = None
    credit: FieldCoordinate | None = None
    balance: FieldCoordinate | None = None


class StructuredTransaction(BaseModel):
    transaction_id: str = Field(default_factory=lambda: str(uuid4()))
    page: int
    row_index: int
    date: str | None = None
    description: str = ""
    debit: Decimal | None = None
    credit: Decimal | None = None
    balance: Decimal | None = None
    coordinates: TransactionCoordinates = Field(default_factory=TransactionCoordinates)
    font_metadata: FontMetadata = Field(default_factory=FontMetadata)
    row_bbox: list[float] = Field(default_factory=list)
    confidence: float = 1.0
    validation_warnings: list[str] = Field(default_factory=list)
    is_continuation: bool = False


class ColumnDefinition(BaseModel):
    name: str
    x_min: float
    x_max: float
    x_center: float


class GroupedRow(BaseModel):
    page: int
    row_index: int
    y_center: float
    y_min: float
    y_max: float
    bbox: list[float]
    spans: list[TextSpan] = Field(default_factory=list)
    text: str = ""
    is_header: bool = False
    is_footer: bool = False


class BankClassification(BaseModel):
    bank: str
    confidence: float
    signals: list[str] = Field(default_factory=list)


class TransactionSummary(BaseModel):
    total_debit: Decimal = Decimal("0")
    total_credit: Decimal = Decimal("0")
    opening_balance: Decimal | None = None
    closing_balance: Decimal | None = None
    transaction_count: int = 0
    validation_passed: bool = True
    validation_issues: list[str] = Field(default_factory=list)


class ParseDebugInfo(BaseModel):
    columns: list[ColumnDefinition] = Field(default_factory=list)
    grouped_row_count: int = 0
    raw_row_count: int = 0
    header_row_index: int | None = None


class TransactionParseResult(BaseModel):
    bank: str
    bank_confidence: float
    transactions: list[StructuredTransaction]
    summary: TransactionSummary
    debug: ParseDebugInfo | None = None
    warnings: list[str] = Field(default_factory=list)
