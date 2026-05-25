from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.pdf_engine.models import TextSpan
from app.shared.models import (
    FieldCoordinate,
    FontMetadata,
    StructuredTransaction,
    TransactionCoordinates,
    TransactionSummary,
)


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


class ParseDebugInfo(BaseModel):
    columns: list[ColumnDefinition] = Field(default_factory=list)
    grouped_row_count: int = 0
    raw_row_count: int = 0
    header_row_index: int | None = None
    table_regions: list[Any] = Field(default_factory=list)
    extraction_mode: str = "native"
    layout_confidence: float | None = None
    ocr_confidence: float | None = None
    header_row_y: float | None = None
    row_segments: list[Any] = Field(default_factory=list)
    bank_layout_version: str | None = None


class TransactionParseResult(BaseModel):
    bank: str
    bank_confidence: float
    transactions: list[StructuredTransaction]
    summary: TransactionSummary
    debug: ParseDebugInfo | None = None
    warnings: list[str] = Field(default_factory=list)
    extraction_mode: str = "native"
    layout_confidence: float | None = None
    ocr_confidence: float | None = None


GroupedRow.model_rebuild()
