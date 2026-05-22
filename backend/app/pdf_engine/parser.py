"""Orchestrates PDF loading and coordinate-aware extraction."""

from pathlib import Path

from app.pdf_engine.extractor import extract_document
from app.pdf_engine.models import DocumentExtraction
from app.pdf_engine.pdf_loader import get_page_count, validate_pdf_bytes


class PdfParser:
    @staticmethod
    def validate_header(header: bytes) -> None:
        validate_pdf_bytes(header)

    @staticmethod
    def page_count(path: Path) -> int:
        return get_page_count(path)

    @staticmethod
    def extract(
        path: Path,
        *,
        statement_id: str | None = None,
        pages: list[int] | None = None,
    ) -> DocumentExtraction:
        return extract_document(path, statement_id=statement_id, page_numbers=pages)
