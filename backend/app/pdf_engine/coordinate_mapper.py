"""
Coordinate utilities for PDF ↔ viewport mapping.
Prepares click-to-edit and invisible text replacement (Phase 4+).
"""

from __future__ import annotations


def bbox_to_rect(bbox: list[float]) -> tuple[float, float, float, float]:
    x0, y0, x1, y1 = bbox
    return x0, y0, x1 - x0, y1 - y0


def normalize_bbox(bbox: list[float], page_width: float, page_height: float) -> list[float]:
    """Return bbox as fractions of page dimensions [0–1]."""
    x0, y0, x1, y1 = bbox
    return [
        x0 / page_width if page_width else 0,
        y0 / page_height if page_height else 0,
        x1 / page_width if page_width else 0,
        y1 / page_height if page_height else 0,
    ]


def pdf_to_viewport(
    bbox: list[float],
    page_height: float,
    scale: float,
    viewport_offset_x: float = 0,
    viewport_offset_y: float = 0,
) -> dict[str, float]:
    """
    Map PDF top-left origin bbox to CSS overlay pixels at given scale.
    """
    x0, y0, x1, y1 = bbox
    return {
        "left": x0 * scale + viewport_offset_x,
        "top": y0 * scale + viewport_offset_y,
        "width": (x1 - x0) * scale,
        "height": (y1 - y0) * scale,
    }


def viewport_to_pdf(
    css_x: float,
    css_y: float,
    scale: float,
    viewport_offset_x: float = 0,
    viewport_offset_y: float = 0,
) -> tuple[float, float]:
    """Inverse map: CSS pixel → PDF coordinate."""
    pdf_x = (css_x - viewport_offset_x) / scale
    pdf_y = (css_y - viewport_offset_y) / scale
    return pdf_x, pdf_y


def scale_bbox(bbox: list[float], scale: float) -> list[float]:
    x0, y0, x1, y1 = bbox
    return [x0 * scale, y0 * scale, x1 * scale, y1 * scale]
