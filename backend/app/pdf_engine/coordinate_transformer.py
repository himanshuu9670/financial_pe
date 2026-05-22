"""
PDF coordinate normalization and insert-point calculation.
PyMuPDF uses top-left origin (same as extraction).
"""

from __future__ import annotations

from app.pdf_engine.edit_models import Alignment, TypographySpec


def normalize_bbox(bbox: list[float], page_width: float, page_height: float) -> list[float]:
    x0, y0, x1, y1 = bbox
    return [
        max(0, min(x0, page_width)),
        max(0, min(y0, page_height)),
        max(0, min(x1, page_width)),
        max(0, min(y1, page_height)),
    ]


def expand_bbox(bbox: list[float], pad: float = 1.0) -> list[float]:
    x0, y0, x1, y1 = bbox
    return [x0 - pad, y0 - pad, x1 + pad, y1 + pad]


def compute_insert_point(
    bbox: list[float],
    text: str,
    typography: TypographySpec,
    *,
    text_width: float | None = None,
) -> tuple[float, float]:
    """
    Compute baseline insert point inside bbox.
    Amount columns in bank statements are typically right-aligned.
    """
    x0, y0, x1, y1 = bbox
    font_size = typography.font_size
    width = text_width if text_width is not None else len(text) * font_size * 0.52
    baseline_y = y1 - max(2, font_size * 0.25)

    if typography.alignment == Alignment.RIGHT:
        x = x1 - width - 0.5
        x = max(x0, x)
    elif typography.alignment == Alignment.CENTER:
        x = x0 + ((x1 - x0) - width) / 2
    else:
        x = x0 + 0.5

    return (round(x, 2), round(baseline_y, 2))


def estimate_text_width(text: str, font_size: float) -> float:
    return len(text) * font_size * 0.52
