"""
Coordinate-aware PDF text extraction using PyMuPDF dict mode.
Preserves spans, lines, blocks, and typography metadata.
"""

from __future__ import annotations

import gc
from pathlib import Path

import fitz

from app.core.config import get_settings
from app.pdf_engine.font_detector import normalize_font_name, primary_font_from_spans
from app.pdf_engine.models import DocumentExtraction, PageExtraction, TextBlock, TextSpan
from app.pdf_engine.pdf_loader import open_pdf
from app.utils.logging import get_logger

logger = get_logger(__name__)

SCANNED_TEXT_THRESHOLD = 20


def _span_from_dict(span: dict) -> TextSpan:
    x0, y0, x1, y1 = span["bbox"]
    return TextSpan(
        text=span.get("text", ""),
        x=round(x0, 2),
        y=round(y0, 2),
        width=round(x1 - x0, 2),
        height=round(y1 - y0, 2),
        font=normalize_font_name(span.get("font")),
        font_size=round(float(span.get("size", 0)), 2),
        bbox=[round(v, 2) for v in span["bbox"]],
        flags=span.get("flags"),
        color=span.get("color"),
    )


def extract_page(page: fitz.Page, page_number: int) -> PageExtraction:
    blocks_out: list[TextBlock] = []
    raw = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)

    for block in raw.get("blocks", []):
        if block.get("type") != 0:
            continue

        block_bbox = block.get("bbox", [0, 0, 0, 0])
        all_spans: list[TextSpan] = []
        line_texts: list[str] = []

        for line in block.get("lines", []):
            line_spans = [_span_from_dict(s) for s in line.get("spans", []) if s.get("text")]
            all_spans.extend(line_spans)
            line_texts.append("".join(s.text for s in line_spans))

        if not all_spans:
            continue

        combined_text = "\n".join(t for t in line_texts if t).strip()
        font, font_size = primary_font_from_spans(
            [{"font": s.font, "size": s.font_size, "text": s.text} for s in all_spans]
        )
        x0, y0, x1, y1 = block_bbox

        blocks_out.append(
            TextBlock(
                text=combined_text,
                x=round(x0, 2),
                y=round(y0, 2),
                width=round(x1 - x0, 2),
                height=round(y1 - y0, 2),
                font=font,
                font_size=font_size,
                bbox=[round(v, 2) for v in block_bbox],
                spans=all_spans,
            )
        )

    rect = page.rect
    return PageExtraction(
        page=page_number,
        width=round(rect.width, 2),
        height=round(rect.height, 2),
        blocks=blocks_out,
    )


def extract_document(
    path: Path,
    *,
    statement_id: str | None = None,
    page_numbers: list[int] | None = None,
) -> DocumentExtraction:
    doc = open_pdf(path)
    warnings: list[str] = []
    pages: list[PageExtraction] = []
    total_span_count = 0

    try:
        settings = get_settings()
        batch_size = max(1, settings.pdf_page_batch_size)
        max_pages = settings.pdf_max_pages_in_memory

        if page_numbers:
            indices = page_numbers
        else:
            indices = list(range(1, min(doc.page_count, max_pages) + 1))
            if doc.page_count > max_pages:
                warnings.append(
                    f"Large PDF ({doc.page_count} pages): extracted first {max_pages} pages. "
                    "Use ?pages= for incremental extraction."
                )

        for batch_start in range(0, len(indices), batch_size):
            batch = indices[batch_start : batch_start + batch_size]
            for num in batch:
                if num < 1 or num > doc.page_count:
                    warnings.append(f"Skipped invalid page number: {num}")
                    continue
                page_data = extract_page(doc[num - 1], num)
                total_span_count += sum(len(b.spans) for b in page_data.blocks)
                pages.append(page_data)
            if len(indices) > batch_size:
                gc.collect()

        is_likely_scanned = total_span_count < SCANNED_TEXT_THRESHOLD
        if is_likely_scanned:
            warnings.append(
                "Very little extractable text detected — document may be scanned. "
                "OCR pipeline will be required (future phase)."
            )

        logger.info(
            "pdf_extracted",
            path=str(path),
            pages=len(pages),
            spans=total_span_count,
            scanned=is_likely_scanned,
        )

        return DocumentExtraction(
            statement_id=statement_id,
            total_pages=doc.page_count,
            pages=pages,
            span_count=total_span_count,
            block_count=sum(len(p.blocks) for p in pages),
            warnings=warnings,
            is_likely_scanned=is_likely_scanned,
        )
    finally:
        doc.close()
