"""Domain models for invisible PDF editing pipeline."""

from __future__ import annotations

from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class Alignment(str, Enum):
    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"


class TypographySpec(BaseModel):
    font: str = "helv"
    font_size: float = 10.0
    color: tuple[float, float, float] = (0.0, 0.0, 0.0)
    alignment: Alignment = Alignment.RIGHT
    char_width_estimate: float | None = None
    line_height: float | None = None


class TargetSpan(BaseModel):
    transaction_id: str
    field: str
    field_id: str
    page: int
    bbox: list[float]
    original_text: str
    new_text: str
    typography: TypographySpec
    pymupdf_font: str = "helv"

    @property
    def font(self) -> str:
        """Compatibility accessor for legacy code and tests expecting `font`.

        Returns the human-facing font name from the `typography` spec.
        """
        return getattr(self.typography, "font", "")


class TextReplacementTarget(BaseModel):
    """Resolved target for overlay replacement."""

    span: TargetSpan
    rect: list[float]  # expanded bbox [x0,y0,x1,y1]
    insert_point: tuple[float, float]
    success: bool = False
    error: str | None = None


class ReplacementResult(BaseModel):
    target: TextReplacementTarget
    applied: bool
    message: str = ""


class VisualValidationMetrics(BaseModel):
    text_match_ratio: float = 1.0
    bbox_overlap_ratio: float = 1.0
    regions_checked: int = 0
    issues: list[str] = Field(default_factory=list)
    passed: bool = True


class ExportResult(BaseModel):
    output_path: str
    replacements_applied: int
    replacements_failed: int
    validation: VisualValidationMetrics
    warnings: list[str] = Field(default_factory=list)
    is_scanned_fallback_recommended: bool = False
