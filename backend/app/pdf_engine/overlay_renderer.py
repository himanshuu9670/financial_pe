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


def draw_replacement_text(page: fitz.Page, target: TextReplacementTarget) -> None:
    span = target.span
    typo = span.typography
    x, y = target.insert_point

    bbox_height = 0.0
    if len(span.bbox) == 4:
        bbox_height = span.bbox[3] - span.bbox[1]
    else:
        bbox_height = target.rect[3] - target.rect[1]

    # Apply a very small dynamic baseline correction based on the text span height.
    # This preserves the existing insert_text() workflow while improving per-span consistency.
    correction = bbox_height * 0.06
    correction = max(0.4, min(correction, 1.0))
    adjusted_point = (x, y - correction)

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
