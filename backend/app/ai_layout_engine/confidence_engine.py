"""
Extraction confidence scoring — OCR, layout, balance consistency.
"""

from __future__ import annotations

from decimal import Decimal

from app.shared.models import StructuredTransaction
from app.ai_layout_engine.models import LayoutAnalysis, RowSegment


def score_layout(layout: LayoutAnalysis) -> float:
    base = layout.bank.confidence * 0.4
    table = 0.0
    if layout.table_regions:
        table = sum(r.confidence for r in layout.table_regions) / len(layout.table_regions) * 0.3
    col = 0.2 if len(layout.columns) >= 3 else 0.05
    ocr = (layout.ocr_confidence or 0.85) * 0.1 if layout.extraction_mode.value == "ocr" else 0.1
    return round(min(0.99, base + table + col + ocr), 2)


def score_transaction(
    txn: StructuredTransaction,
    *,
    layout_confidence: float,
    row_segments: list[RowSegment],
) -> float:
    conf = layout_confidence * 0.5 + txn.confidence * 0.2

    if txn.date:
        conf += 0.1
    if txn.debit or txn.credit:
        conf += 0.1
    if txn.balance is not None:
        conf += 0.1

    for seg in row_segments:
        if seg.page == txn.page and abs(seg.row_index - txn.row_index) <= 1:
            conf = conf * 0.7 + seg.confidence * 0.3
            break

    if txn.validation_warnings:
        conf -= 0.15 * len(txn.validation_warnings)

    return round(max(0.1, min(0.99, conf)), 2)


def apply_confidence_to_transactions(
    transactions: list[StructuredTransaction],
    layout: LayoutAnalysis,
    row_segments: list[RowSegment],
) -> None:
    lc = score_layout(layout)
    for txn in transactions:
        txn.confidence = score_transaction(txn, layout_confidence=lc, row_segments=row_segments)
