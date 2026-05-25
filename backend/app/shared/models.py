"""
Shared domain DTOs — used by ai_engine, financial_engine, and pdf_engine.
Extracted to break circular dependencies.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class FieldCoordinate(BaseModel):
    """Coordinate of a single field/cell in PDF."""

    text: str
    x: float
    y: float
    width: float
    height: float
    bbox: list[float]
    field_id: str = Field(default_factory=lambda: str(uuid4()))
    font: str = "Unknown"
    font_size: float = 0.0
    color: int | None = None


class FontMetadata(BaseModel):
    """Font properties for a row or transaction."""

    primary_font: str = "Unknown"
    primary_size: float = 0.0
    fields: dict[str, str] = Field(default_factory=dict)


class TransactionCoordinates(BaseModel):
    """Coordinates of all fields in a transaction row."""

    date: FieldCoordinate | None = None
    description: FieldCoordinate | None = None
    debit: FieldCoordinate | None = None
    credit: FieldCoordinate | None = None
    balance: FieldCoordinate | None = None


class StructuredTransaction(BaseModel):
    """Parsed transaction with coordinates and metadata."""

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


class TransactionSummary(BaseModel):
    """Summary statistics for a set of transactions."""

    total_debit: Decimal = Decimal("0")
    total_credit: Decimal = Decimal("0")
    opening_balance: Decimal | None = None
    closing_balance: Decimal | None = None
    transaction_count: int = 0
    validation_passed: bool = True
    validation_issues: list[str] = Field(default_factory=list)
