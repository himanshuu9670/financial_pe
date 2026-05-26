"""
Vector-safe overlay rendering via PyMuPDF redaction + text insertion.
"""

from __future__ import annotations

import fitz

from app.pdf_engine.edit_models import TextReplacementTarget
from app.utils.logging import get_logger

logger = get_logger(__name__)


def redact_region(page: fitz.Page, rect: list[float], *, apply: bool = True) -> None:
    page.add_redact_annot(fitz.Rect(rect), fill=(1, 1, 1))
    if apply:
        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)


def batch_redact_page(page: fitz.Page, rects: list[list[float]]) -> None:
    for rect in rects:
        page.add_redact_annot(fitz.Rect(rect), fill=(1, 1, 1))
    if rects:
        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)


def draw_replacement_text(
    page: fitz.Page,
    target: TextReplacementTarget,
    *,
    row_baseline_y: float | None = None,
    row_rect_height: float | None = None,
) -> None:
    span = target.span
    typo = span.typography
    x, y = target.insert_point
    if row_baseline_y is not None:
        y = row_baseline_y

    bbox_height = 0.0
    if len(span.bbox) == 4:
        bbox_height = span.bbox[3] - span.bbox[1]
        original_right_edge = span.bbox[2]
    else:
        bbox_height = target.rect[3] - target.rect[1]
        original_right_edge = target.rect[2]

    rect_height = row_rect_height if row_rect_height is not None else target.rect[3] - target.rect[1]
    baseline_adjustment = rect_height * 0.05
    baseline_adjustment = min(max(baseline_adjustment, 0.5), 1.25)
    adjusted_y = y - baseline_adjustment

    try:
        text_width = fitz.get_text_length(
            span.new_text,
            fontname="helv",
            fontsize=typo.font_size,
        )
        adjusted_x = round(original_right_edge - text_width, 2)
        if span.new_text.startswith("-"):
            adjusted_x += 1.0
    except Exception:
        adjusted_x = x

    adjusted_point = (adjusted_x, adjusted_y)

    try:
        page.insert_text(
            adjusted_point,
            span.new_text,
            fontname="helv",
            fontsize=typo.font_size,
            color=typo.color,
            render_mode=0,
        )
    except Exception as exc:
        logger.warning(
            "insert_text_failed_fallback",
            font="helv",
            error=str(exc),
        )
        page.insert_text(
            adjusted_point,
            span.new_text,
            fontname="helv",
            fontsize=typo.font_size,
            color=typo.color,
        )
