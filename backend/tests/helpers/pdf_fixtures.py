"""Generate synthetic PDF fixtures for QA (no bank templates required)."""

from __future__ import annotations

from pathlib import Path

import fitz


def write_minimal_native_pdf(path: Path, *, pages: int = 1) -> Path:
    doc = fitz.open()
    for i in range(pages):
        page = doc.new_page(width=595, height=842)
        y = 72
        page.insert_text((72, y), f"Page {i + 1} — Test Bank Statement", fontsize=12)
        y += 24
        page.insert_text((72, y), "01/01/2024  SAMPLE DEBIT", fontsize=10)
        page.insert_text((400, y), "1,000.00", fontsize=10)
        y += 16
        page.insert_text((72, y), "02/01/2024  SAMPLE CREDIT", fontsize=10)
        page.insert_text((400, y), "500.00", fontsize=10)
    path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(path))
    doc.close()
    return path


def write_low_text_pdf(path: Path) -> Path:
    """Nearly blank page — triggers scanned/OCR heuristics."""
    doc = fitz.open()
    doc.new_page(width=595, height=842)
    path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(path))
    doc.close()
    return path


def write_multiline_description_pdf(path: Path) -> Path:
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text(
        (72, 72),
        "LONG DESCRIPTION LINE ONE CONTINUES ON NEXT VISUAL ROW",
        fontsize=9,
    )
    page.insert_text((72, 100), "SECOND ROW AMOUNT 250.00", fontsize=10)
    path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(path))
    doc.close()
    return path


def generate_all_fixtures(base_dir: Path) -> list[Path]:
    base_dir.mkdir(parents=True, exist_ok=True)
    paths = [
        write_minimal_native_pdf(base_dir / "minimal_native.pdf"),
        write_minimal_native_pdf(base_dir / "multi_page.pdf", pages=3),
        write_low_text_pdf(base_dir / "low_text_scan_like.pdf"),
        write_multiline_description_pdf(base_dir / "multiline_rows.pdf"),
    ]
    return paths
