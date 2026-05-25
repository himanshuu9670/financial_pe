"""
Hybrid extraction: native text layer → OCR fallback → layout intelligence → transactions.
"""

from __future__ import annotations

from pathlib import Path

from app.cache.ocr_cache import ocr_cache
from app.cache.extraction_cache import extraction_cache

from app.ai_engine.models import ParseDebugInfo, TransactionParseResult
from app.ai_engine.pipeline import run_transaction_pipeline
from app.ai_layout_engine.confidence_engine import apply_confidence_to_transactions
from app.ai_layout_engine.layout_detector import analyze_layout
from app.ai_layout_engine.models import ExtractionMode, IntelligenceDebugPayload, LayoutAnalysis
from app.ai_layout_engine.row_segmenter import segment_rows
from app.ai_layout_engine.bank_signature_engine import fingerprint_bank
from app.ocr_engine.ocr_processor import TesseractOcrProcessor, ocr_extract_document
from app.ocr_engine.scanned_pdf_detector import (
    ScanDetectionResult,
    detect_from_document_stats,
    detect_scanned_pdf,
)
from app.pdf_engine.extractor import extract_document
from app.pdf_engine.models import DocumentExtraction
from app.utils.logging import get_logger

logger = get_logger(__name__)

def hybrid_extract_document(
    path: Path,
    *,
    statement_id: str | None = None,
    page_numbers: list[int] | None = None,
    force_ocr: bool = False,
    use_cache: bool = True,
) -> tuple[DocumentExtraction, ExtractionMode, float | None, ScanDetectionResult]:
    scan = detect_scanned_pdf(path)
    native_cached = extraction_cache.get_native(path, page_numbers) if use_cache else None
    if native_cached:
        native = DocumentExtraction.model_validate(native_cached["document"])
    else:
        native = extract_document(path, statement_id=statement_id, page_numbers=page_numbers)
        if use_cache:
            extraction_cache.set_native(path, native, page_numbers)

    total_chars = sum(len(b.text) for p in native.pages for b in p.blocks)
    scan = detect_from_document_stats(
        native.span_count,
        total_chars,
        is_likely_scanned=native.is_likely_scanned or scan.needs_ocr,
    )

    mode = ExtractionMode.NATIVE
    ocr_conf: float | None = None

    if force_ocr or scan.needs_ocr:
        from app.monitoring.ocr_metrics import record_pages, track_ocr_run

        cached_ocr = ocr_cache.get_document(path, page_numbers) if use_cache else None
        if cached_ocr:
            document, ocr_conf = cached_ocr
            record_pages(len(document.pages))
        else:
            processor = TesseractOcrProcessor()
            if processor.is_available():
                with track_ocr_run():
                    document, ocr_conf = ocr_extract_document(
                        path,
                        statement_id=statement_id,
                        page_numbers=page_numbers,
                    )
                record_pages(len(document.pages))
                if use_cache:
                    ocr_cache.set_document(
                        path,
                        document,
                        ocr_conf,
                        page_numbers=page_numbers,
                        scan=scan.model_dump(mode="json"),
                    )
            else:
                from app.monitoring.ocr_metrics import record_failure

                record_failure("tesseract_unavailable")
                logger.warning("ocr_unavailable_using_native")
                document = native
                document.warnings.append("OCR requested but Tesseract unavailable — using native layer.")
                mode = ExtractionMode.HYBRID
                return document, mode, None, scan

        mode = ExtractionMode.OCR
        logger.info("hybrid_ocr_used", statement_id=statement_id, ocr_confidence=ocr_conf)
    else:
        document = native

    return document, mode, ocr_conf, scan


def run_intelligent_pipeline(
    document: DocumentExtraction,
    *,
    extraction_mode: ExtractionMode = ExtractionMode.NATIVE,
    ocr_confidence: float | None = None,
    include_debug: bool = False,
) -> tuple[TransactionParseResult, LayoutAnalysis, IntelligenceDebugPayload | None]:
    layout = analyze_layout(
        document,
        extraction_mode=extraction_mode,
        ocr_confidence=ocr_confidence,
    )

    bank_sig = fingerprint_bank(document)
    if bank_sig.bank != "UNKNOWN":
        layout.bank = bank_sig

    result = run_transaction_pipeline(document, include_debug=include_debug)
    result.bank = layout.bank.bank
    result.bank_confidence = layout.bank.confidence
    result.extraction_mode = extraction_mode.value
    result.layout_confidence = layout.layout_confidence
    result.ocr_confidence = ocr_confidence

    row_segments = segment_rows(document)
    apply_confidence_to_transactions(result.transactions, layout, row_segments)

    intel_debug: IntelligenceDebugPayload | None = None
    if include_debug:
        result.debug = ParseDebugInfo(
            columns=layout.columns[:20] or (result.debug.columns if result.debug else []),
            grouped_row_count=len(row_segments),
            raw_row_count=len(row_segments),
            header_row_index=None,
            table_regions=layout.table_regions,
            extraction_mode=extraction_mode.value,
            layout_confidence=layout.layout_confidence,
            ocr_confidence=ocr_confidence,
            header_row_y=layout.header_row_y,
            row_segments=row_segments[:100],
            bank_layout_version=layout.bank.layout_version,
        )
        intel_debug = IntelligenceDebugPayload(
            layout=layout,
            row_segments=row_segments[:150],
            column_boundaries=layout.columns,
            ocr_word_count=document.span_count if extraction_mode == ExtractionMode.OCR else 0,
            native_span_count=document.span_count,
        )

    for w in layout.warnings:
        if w not in result.warnings:
            result.warnings.append(w)

    if layout.unknown_bank_adaptive:
        result.warnings.append("Adaptive parsing for unrecognized bank layout.")

    return result, layout, intel_debug
