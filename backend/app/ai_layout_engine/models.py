"""Layout intelligence domain models."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

from app.ai_engine.models import ColumnDefinition


class ExtractionMode(str, Enum):
    NATIVE = "native"
    OCR = "ocr"
    HYBRID = "hybrid"


class BankSignatureMatch(BaseModel):
    bank: str
    confidence: float
    layout_version: str = "generic_v1"
    signals: list[str] = Field(default_factory=list)


class TableRegion(BaseModel):
    page: int
    bbox: list[float]
    row_count_estimate: int = 0
    confidence: float = 0.0


class LayoutAnalysis(BaseModel):
    bank: BankSignatureMatch
    extraction_mode: ExtractionMode
    table_regions: list[TableRegion] = Field(default_factory=list)
    columns: list[ColumnDefinition] = Field(default_factory=list)
    header_row_y: float | None = None
    layout_confidence: float = 0.0
    ocr_confidence: float | None = None
    is_scanned: bool = False
    unknown_bank_adaptive: bool = False
    warnings: list[str] = Field(default_factory=list)


class RowSegment(BaseModel):
    page: int
    row_index: int
    bbox: list[float]
    text: str
    span_count: int
    confidence: float = 1.0


class IntelligenceDebugPayload(BaseModel):
    layout: LayoutAnalysis
    row_segments: list[RowSegment] = Field(default_factory=list)
    column_boundaries: list[ColumnDefinition] = Field(default_factory=list)
    ocr_word_count: int = 0
    native_span_count: int = 0
