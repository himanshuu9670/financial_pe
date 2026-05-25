"""Orchestrates full layout analysis on a DocumentExtraction."""

from __future__ import annotations

from app.ai_layout_engine.bank_signature_engine import fingerprint_bank, _document_text
from app.ai_layout_engine.column_mapper import map_columns
from app.ai_layout_engine.header_detector import detect_header_y
from app.ai_layout_engine.models import ExtractionMode, LayoutAnalysis
from app.ai_layout_engine.table_detector import detect_table_regions
from app.ai_layout_engine.template_matcher import match_template
from app.ai_layout_engine.confidence_engine import score_layout
from app.pdf_engine.models import DocumentExtraction


def analyze_layout(
    document: DocumentExtraction,
    *,
    extraction_mode: ExtractionMode = ExtractionMode.NATIVE,
    ocr_confidence: float | None = None,
) -> LayoutAnalysis:
    bank = fingerprint_bank(document)
    full_text = _document_text(document).lower()
    bank = match_template(bank, full_text)

    header_y = detect_header_y(document)
    tables = detect_table_regions(document, header_y=header_y)
    columns = map_columns(document)

    warnings: list[str] = []
    unknown_adaptive = bank.bank == "UNKNOWN"

    if unknown_adaptive:
        warnings.append("Unknown bank — adaptive column/row detection active.")
    if document.is_likely_scanned:
        warnings.append("Low native text density — OCR may improve results.")
    if len(columns) < 3:
        warnings.append("Few columns detected — layout may be irregular.")

    layout = LayoutAnalysis(
        bank=bank,
        extraction_mode=extraction_mode,
        table_regions=tables,
        columns=columns,
        header_row_y=header_y,
        ocr_confidence=ocr_confidence,
        is_scanned=document.is_likely_scanned,
        unknown_bank_adaptive=unknown_adaptive,
        warnings=warnings,
    )
    layout.layout_confidence = score_layout(layout)
    return layout
