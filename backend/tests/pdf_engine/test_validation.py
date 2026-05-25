"""PDF engine — malformed/corrupt/empty inputs."""

import pytest

from app.pdf_engine.exceptions import PdfCorruptedError, PdfValidationError
from app.pdf_engine.pdf_loader import open_pdf, validate_pdf_bytes


def test_rejects_non_pdf_header():
    with pytest.raises(PdfValidationError):
        validate_pdf_bytes(b"NOTPDFxx")


def test_rejects_empty_bytes():
    with pytest.raises(PdfValidationError):
        validate_pdf_bytes(b"")


def test_opens_minimal_pdf(minimal_pdf_path):
    doc = open_pdf(minimal_pdf_path)
    try:
        assert doc.page_count >= 1
    finally:
        doc.close()


def test_corrupt_file_raises(tmp_path):
    path = tmp_path / "bad.pdf"
    path.write_bytes(b"%PDF-1.4\n% corrupted body without valid xref")
    with pytest.raises((PdfCorruptedError, PdfValidationError)):
        open_pdf(path)


def test_missing_file_raises(tmp_path):
    with pytest.raises(PdfValidationError):
        open_pdf(tmp_path / "missing.pdf")
