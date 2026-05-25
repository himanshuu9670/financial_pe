"""Phase 6 — layout intelligence and OCR detection tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.ai_layout_engine.bank_signature_engine import fingerprint_bank
from app.ai_layout_engine.column_mapper import map_columns
from app.ai_layout_engine.layout_detector import analyze_layout
from app.ai_layout_engine.models import ExtractionMode
from app.ocr_engine.scanned_pdf_detector import detect_from_document_stats
from app.pdf_engine.models import DocumentExtraction, PageExtraction, TextBlock, TextSpan


def _span(text: str, x: float, y: float) -> TextSpan:
    return TextSpan(
        text=text,
        x=x,
        y=y,
        width=50,
        height=10,
        font="Helvetica",
        font_size=10,
        bbox=[x, y, x + 50, y + 10],
    )


def _sample_axis_statement() -> DocumentExtraction:
    blocks = [
        TextBlock(
            text="AXIS BANK LTD",
            x=10,
            y=10,
            width=100,
            height=10,
            font="Helvetica",
            font_size=12,
            bbox=[10, 10, 110, 20],
            spans=[_span("AXIS BANK LTD", 10, 10)],
        ),
        TextBlock(
            text="Tran Date Particulars Withdrawal Deposit Balance",
            x=10,
            y=80,
            width=400,
            height=10,
            font="Helvetica",
            font_size=9,
            bbox=[10, 80, 410, 90],
            spans=[
                _span("Tran Date", 10, 80),
                _span("Particulars", 100, 80),
                _span("Withdrawal", 200, 80),
                _span("Deposit", 280, 80),
                _span("Balance", 360, 80),
            ],
        ),
        TextBlock(
            text="01/01/2024 UPI PAYMENT 500.00 10000.00",
            x=10,
            y=100,
            width=400,
            height=10,
            font="Helvetica",
            font_size=9,
            bbox=[10, 100, 410, 110],
            spans=[
                _span("01/01/2024", 10, 100),
                _span("UPI PAYMENT", 100, 100),
                _span("500.00", 200, 100),
                _span("10000.00", 360, 100),
            ],
        ),
    ]
    page = PageExtraction(page=1, width=595, height=842, blocks=blocks)
    return DocumentExtraction(
        statement_id="test",
        total_pages=1,
        pages=[page],
        span_count=sum(len(b.spans) for b in blocks),
        block_count=len(blocks),
    )


def test_fingerprint_axis_bank():
    doc = _sample_axis_statement()
    match = fingerprint_bank(doc)
    assert match.bank == "AXIS_BANK"
    assert match.confidence > 0.3


def test_layout_analysis_columns():
    doc = _sample_axis_statement()
    layout = analyze_layout(doc, extraction_mode=ExtractionMode.NATIVE)
    assert layout.layout_confidence > 0
    assert len(layout.columns) >= 1


def test_scanned_detection_low_text():
    result = detect_from_document_stats(5, 10, is_likely_scanned=True)
    assert result.needs_ocr is True


def test_map_columns_on_sample():
    doc = _sample_axis_statement()
    cols = map_columns(doc)
    names = {c.name for c in cols}
    assert len(names) >= 1


@pytest.mark.skipif(
    not Path("/usr/bin/tesseract").exists() and not _tesseract_available(),
    reason="Tesseract not installed",
)
def test_ocr_processor_available():
    from app.ocr_engine.ocr_processor import TesseractOcrProcessor

    assert TesseractOcrProcessor().is_available()


def _tesseract_available() -> bool:
    try:
        import pytesseract

        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False
