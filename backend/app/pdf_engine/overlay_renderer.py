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
    adjusted_point = (x, y - 1.25)

    try:
        page.insert_text(
            adjusted_point,
            span.new_text,
            fontname=span.pymupdf_font,
            fontsize=typo.font_size,
            color=typo.color,
            render_mode=0,
        )
    except Exception as exc:
        logger.warning(
            "insert_text_failed_fallback",
            font=span.pymupdf_font,
            error=str(exc),
        )
        page.insert_text(
            adjusted_point,
            span.new_text,
            fontname="helv",
            fontsize=typo.font_size,
            color=typo.color,
        )
