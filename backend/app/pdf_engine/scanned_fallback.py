"""
Scanned PDF fallback architecture — OCR-based coordinate reconstruction (Phase 6+).

When text layer is unavailable:
  1. ocr_engine renders page to image
  2. Tesseract returns word boxes
  3. span_adapter builds synthetic FieldCoordinates
  4. Same text_replacer pipeline applies overlays on raster underlay (not implemented)
"""

from pathlib import Path

from app.pdf_engine.edit_models import ExportResult, VisualValidationMetrics


def export_via_ocr_overlay(
    source_pdf: Path,
    output_pdf: Path,
) -> ExportResult:
    raise NotImplementedError(
        "OCR-based invisible editing is not implemented. "
        "Use text-based PDF statements or wait for Phase 6 OCR pipeline."
    )


def needs_ocr_fallback(extraction_json: dict | None, span_count: int) -> bool:
    if span_count < 20:
        return True
    if extraction_json and extraction_json.get("is_likely_scanned"):
        return True
    return False
