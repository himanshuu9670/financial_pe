"""Aggregate confidence from OCR, layout, financial, and semantic signals."""

from __future__ import annotations

from app.shared.models import StructuredTransaction
from app.ai_engine.models import TransactionParseResult
from app.ai_intelligence.models import CategoryResult, ConfidenceBreakdown


def boost_confidence(
    parse_result: TransactionParseResult | None,
    categories: list[CategoryResult],
    transactions: list[StructuredTransaction],
    *,
    ocr_confidence: float | None = None,
    layout_confidence: float | None = None,
) -> ConfidenceBreakdown:
    factors: list[str] = []

    ocr = ocr_confidence
    layout = layout_confidence or (parse_result.layout_confidence if parse_result else None)
    financial = 0.85
    semantic = 0.0

    if parse_result:
        if parse_result.summary.validation_passed:
            financial = 0.95
            factors.append("balance_chain_valid")
        else:
            financial = 0.45
            factors.append("validation_issues")

    if categories:
        semantic = sum(c.confidence for c in categories) / len(categories)
        factors.append("semantic_categories")

    txn_conf = 0.0
    if transactions:
        txn_conf = sum(t.confidence for t in transactions) / len(transactions)

    parts = [p for p in [ocr, layout, financial, semantic, txn_conf] if p is not None]
    overall = sum(parts) / len(parts) if parts else 0.5

    if ocr is not None and ocr < 0.5:
        factors.append("low_ocr")
        overall *= 0.85
    if layout is not None and layout < 0.5:
        factors.append("weak_layout")

    return ConfidenceBreakdown(
        overall=round(min(0.99, overall), 2),
        ocr=round(ocr, 2) if ocr is not None else None,
        layout=round(layout, 2) if layout is not None else None,
        financial=round(financial, 2),
        semantic=round(semantic, 2),
        factors=factors,
    )
