"""
Pixel-accurate bounding box detection and isolation for text replacement regions.
"""

from __future__ import annotations

import fitz

from app.pdf_engine.coordinate_transformer import compute_insert_point, estimate_text_width, expand_bbox
from app.pdf_engine.edit_models import Alignment, TargetSpan, TextReplacementTarget, TypographySpec
from app.pdf_engine.font_mapper import resolve_pymupdf_font


def detect_replacement_region(
    span: TargetSpan,
    page: fitz.Page,
    *,
    pad: float = 1.5,
) -> TextReplacementTarget:
    rect = page.rect
    bbox = span.bbox
    if len(bbox) < 4:
        return TextReplacementTarget(
            span=span,
            rect=[0, 0, 0, 0],
            insert_point=(0, 0),
            success=False,
            error="Invalid bbox",
        )

    expanded = expand_bbox(bbox, pad)
    x0, y0, x1, y1 = expanded
    x0 = max(0, min(x0, rect.width))
    y0 = max(0, min(y0, rect.height))
    x1 = max(x0 + 1, min(x1, rect.width))
    y1 = max(y0 + 1, min(y1, rect.height))
    expanded = [x0, y0, x1, y1]

    typography = span.typography
    pymupdf_font = span.pymupdf_font or resolve_pymupdf_font(typography.font)
    text_width = estimate_text_width(span.new_text, typography.font_size)
    insert = compute_insert_point(expanded, span.new_text, typography, text_width=text_width)

    return TextReplacementTarget(
        span=span,
        rect=expanded,
        insert_point=insert,
        success=True,
    )


def infer_alignment_from_bbox(bbox: list[float], page_width: float) -> Alignment:
    x0, _, x1, _ = bbox
    center = (x0 + x1) / 2
    if center > page_width * 0.55:
        return Alignment.RIGHT
    if center < page_width * 0.35:
        return Alignment.LEFT
    return Alignment.RIGHT
