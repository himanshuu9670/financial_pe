from pathlib import Path

import fitz

from app.pdf_engine.exceptions import (
    PdfCorruptedError,
    PdfEncryptedError,
    PdfValidationError,
)

PDF_MAGIC = b"%PDF"
MAX_SCAN_BYTES = 8


def validate_pdf_bytes(header: bytes) -> None:
    if not header.startswith(PDF_MAGIC):
        raise PdfValidationError("File is not a valid PDF (missing %PDF header)")


def open_pdf(path: Path) -> fitz.Document:
    if not path.exists():
        raise PdfValidationError(f"PDF not found: {path}")

    try:
        doc = fitz.open(path)
    except Exception as exc:
        raise PdfCorruptedError(f"Cannot open PDF: {exc}") from exc

    if doc.is_encrypted:
        if not doc.authenticate(""):
            doc.close()
            raise PdfEncryptedError("PDF is password-protected")
    if doc.page_count == 0:
        doc.close()
        raise PdfValidationError("PDF has no pages")

    return doc


def get_page_count(path: Path) -> int:
    doc = open_pdf(path)
    try:
        return doc.page_count
    finally:
        doc.close()
