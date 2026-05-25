from uuid import UUID

from pydantic import BaseModel, Field


class BankSignatureSchema(BaseModel):
    bank: str
    confidence: float
    layout_version: str = "generic_v1"
    signals: list[str] = Field(default_factory=list)


class TableRegionSchema(BaseModel):
    page: int
    bbox: list[float]
    row_count_estimate: int = 0
    confidence: float = 0.0


class ColumnSchema(BaseModel):
    name: str
    x_min: float
    x_max: float
    x_center: float


class RowSegmentSchema(BaseModel):
    page: int
    row_index: int
    bbox: list[float]
    text: str
    span_count: int
    confidence: float = 1.0


class LayoutAnalysisSchema(BaseModel):
    bank: BankSignatureSchema
    extraction_mode: str
    table_regions: list[TableRegionSchema] = Field(default_factory=list)
    columns: list[ColumnSchema] = Field(default_factory=list)
    header_row_y: float | None = None
    layout_confidence: float = 0.0
    ocr_confidence: float | None = None
    is_scanned: bool = False
    unknown_bank_adaptive: bool = False
    warnings: list[str] = Field(default_factory=list)


class IntelligenceAnalysisResponse(BaseModel):
    statement_id: UUID
    layout: LayoutAnalysisSchema
    transaction_count: int
    layout_confidence: float
    ocr_confidence: float | None = None
    extraction_mode: str
    bank: str
    bank_confidence: float
    columns: list[ColumnSchema] = Field(default_factory=list)
    table_regions: list[TableRegionSchema] = Field(default_factory=list)
    row_segments: list[RowSegmentSchema] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    cached: bool = False
