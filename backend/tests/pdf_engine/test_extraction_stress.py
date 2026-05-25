"""PDF extraction stress — multi-page and low-text heuristics."""

from app.pdf_engine.extractor import extract_document
from tests.helpers.pdf_fixtures import (
    write_low_text_pdf,
    write_minimal_native_pdf,
    write_multiline_description_pdf,
)


def test_extract_minimal_native(tmp_path):
    path = write_minimal_native_pdf(tmp_path / "native.pdf")
    doc = extract_document(path)
    assert doc.total_pages == 1
    assert doc.span_count > 0


def test_extract_multi_page(tmp_path):
    path = write_minimal_native_pdf(tmp_path / "multi.pdf", pages=3)
    doc = extract_document(path)
    assert doc.total_pages == 3


def test_low_text_may_flag_scanned(tmp_path):
    path = write_low_text_pdf(tmp_path / "low.pdf")
    doc = extract_document(path)
    assert doc.span_count == 0 or doc.is_likely_scanned


def test_multiline_pdf_extracts_spans(tmp_path):
    path = write_multiline_description_pdf(tmp_path / "ml.pdf")
    doc = extract_document(path)
    assert doc.span_count >= 1
