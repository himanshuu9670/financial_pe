"""
Detect image-only / low-text PDFs that require OCR fallback.
"""

from __future__ import annotations

from pathlib import Path

import fitz

from pydantic import BaseModel, Field

from app.pdf_engine.extractor import SCANNED_TEXT_THRESHOLD

MIN_CHARS_PER_PAGE = 15
MIN_AVG_CONFIDENCE = 40


class ScanDetectionResult(BaseModel):
    needs_ocr: bool
    reason: str
    total_text_chars: int = 0
    span_count: int = 0
    image_page_ratio: float = 0.0
    avg_native_quality: float = 1.0
    signals: list[str] = Field(default_factory=list)


def detect_from_document_stats(
    span_count: int,
    total_chars: int,
    *,
    is_likely_scanned: bool = False,
) -> ScanDetectionResult:
    signals: list[str] = []
    needs = is_likely_scanned or (
        span_count < SCANNED_TEXT_THRESHOLD
        and total_chars < MIN_CHARS_PER_PAGE * 2
    )

    if span_count < SCANNED_TEXT_THRESHOLD:
        signals.append(f"low_span_count:{span_count}")
    if total_chars < MIN_CHARS_PER_PAGE * 2:
        signals.append(f"low_char_count:{total_chars}")
        needs = True

    reason = "native_text_sufficient"
    if needs:
        reason = "insufficient_native_text_layer"

    return ScanDetectionResult(
        needs_ocr=needs,
        reason=reason,
        span_count=span_count,
        total_text_chars=total_chars,
        signals=signals,
    )


def detect_scanned_pdf(path: Path, *, sample_pages: int = 3) -> ScanDetectionResult:
    doc = fitz.open(path)
    try:
        total_chars = 0
        span_count = 0
        image_pages = 0
        pages_to_check = min(doc.page_count, sample_pages)

        for i in range(pages_to_check):
            page = doc[i]
            text = page.get_text("text") or ""
            total_chars += len(text.strip())
            blocks = page.get_text("dict").get("blocks", [])
            for block in blocks:
                if block.get("type") == 0:
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            if span.get("text", "").strip():
                                span_count += 1
                elif block.get("type") == 1:
                    image_pages += 1

        image_ratio = image_pages / max(1, pages_to_check * 5)
        native = detect_from_document_stats(span_count, total_chars)
        native.image_page_ratio = round(image_ratio, 2)

        if image_ratio > 0.5 and span_count < SCANNED_TEXT_THRESHOLD * 2:
            native.needs_ocr = True
            native.reason = "image_heavy_low_text"
            native.signals.append("high_image_block_ratio")

        return native
    finally:
        doc.close()
