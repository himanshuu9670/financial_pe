"""
Rebuild DocumentExtraction-compatible spans from OCR word boxes.
"""

from __future__ import annotations

from app.pdf_engine.font_detector import normalize_font_name
from app.pdf_engine.models import DocumentExtraction, PageExtraction, TextBlock, TextSpan


def spans_to_page(
    words: list[dict],
    page_number: int,
    page_width: float,
    page_height: float,
) -> PageExtraction:
    """Group words into line blocks by y proximity."""
    if not words:
        return PageExtraction(page=page_number, width=page_width, height=page_height, blocks=[])

    sorted_words = sorted(words, key=lambda w: (w["y"], w["x"]))
    lines: list[list[dict]] = []
    current: list[dict] = []
    last_y: float | None = None
    median_h = sorted(w["height"] for w in sorted_words)[len(sorted_words) // 2] or 12

    for w in sorted_words:
        if last_y is not None and abs(w["y"] - last_y) > median_h * 1.2:
            if current:
                lines.append(current)
            current = []
        current.append(w)
        last_y = w["y"]
    if current:
        lines.append(current)

    blocks: list[TextBlock] = []
    for line_words in lines:
        line_words.sort(key=lambda w: w["x"])
        spans: list[TextSpan] = []
        for w in line_words:
            spans.append(
                TextSpan(
                    text=w["text"],
                    x=w["x"],
                    y=w["y"],
                    width=w["width"],
                    height=w["height"],
                    font=normalize_font_name("OCR"),
                    font_size=round(w["height"] * 0.85, 2),
                    bbox=w["bbox"],
                )
            )
        if not spans:
            continue
        x0 = min(s["bbox"][0] for s in spans)
        y0 = min(s["bbox"][1] for s in spans)
        x1 = max(s["bbox"][2] for s in spans)
        y1 = max(s["bbox"][3] for s in spans)
        text = " ".join(s.text for s in spans)
        blocks.append(
            TextBlock(
                text=text,
                x=round(x0, 2),
                y=round(y0, 2),
                width=round(x1 - x0, 2),
                height=round(y1 - y0, 2),
                font="OCR",
                font_size=spans[0].font_size,
                bbox=[round(x0, 2), round(y0, 2), round(x1, 2), round(y1, 2)],
                spans=spans,
            )
        )

    return PageExtraction(
        page=page_number,
        width=page_width,
        height=page_height,
        blocks=blocks,
    )


def build_document(
    pages: list[PageExtraction],
    *,
    statement_id: str | None = None,
    ocr_confidence: float,
    warnings: list[str] | None = None,
) -> DocumentExtraction:
    span_count = sum(len(b.spans) for p in pages for b in p.blocks)
    return DocumentExtraction(
        statement_id=statement_id,
        total_pages=len(pages),
        pages=pages,
        span_count=span_count,
        block_count=sum(len(p.blocks) for p in pages),
        warnings=warnings or ["Extracted via OCR pipeline."],
        is_likely_scanned=True,
    )
