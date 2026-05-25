"""OCR resilience — detector and confidence without full Tesseract run."""

import pytest

from app.ocr_engine.ocr_processor import TesseractOcrProcessor
from app.ocr_engine.scanned_pdf_detector import detect_scanned_pdf
from tests.helpers.pdf_fixtures import write_low_text_pdf, write_minimal_native_pdf


def test_native_pdf_not_scanned(tmp_path):
    path = write_minimal_native_pdf(tmp_path / "native.pdf")
    result = detect_scanned_pdf(path)
    assert result.needs_ocr is False


def test_low_text_pdf_likely_scanned(tmp_path):
    path = write_low_text_pdf(tmp_path / "blankish.pdf")
    result = detect_scanned_pdf(path)
    assert result.needs_ocr is True


@pytest.mark.skipif(
    not TesseractOcrProcessor().is_available(),
    reason="Tesseract not installed",
)
def test_tesseract_available_gate():
    assert TesseractOcrProcessor().is_available()
