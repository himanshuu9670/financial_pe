"""Smart UX suggestions for parsing, edits, and export readiness."""

from __future__ import annotations

import uuid

from app.ai_engine.models import TransactionParseResult
from app.ai_intelligence.models import (
    AnomalyFlag,
    ConfidenceBreakdown,
    SmartCorrection,
    SmartSuggestion,
)


def build_suggestions(
    *,
    parse_result: TransactionParseResult | None,
    anomalies: list[AnomalyFlag],
    corrections: list[SmartCorrection],
    confidence: ConfidenceBreakdown,
) -> list[SmartSuggestion]:
    suggestions: list[SmartSuggestion] = []

    for corr in corrections[:10]:
        suggestions.append(
            SmartSuggestion(
                id=str(uuid.uuid4())[:8],
                severity="medium",
                title=f"Fix {corr.field}",
                message=f"Suggest changing '{corr.original}' → '{corr.corrected}' ({corr.reason})",
                action="apply_correction",
                transaction_id=corr.transaction_id,
            )
        )

    for anom in anomalies:
        if anom.severity in ("high", "medium"):
            suggestions.append(
                SmartSuggestion(
                    id=str(uuid.uuid4())[:8],
                    severity=anom.severity,
                    title=anom.anomaly_type.replace("_", " ").title(),
                    message=anom.message,
                    action="review_transaction",
                    transaction_id=anom.transaction_id,
                )
            )

    if confidence.overall < 0.6:
        suggestions.append(
            SmartSuggestion(
                id=str(uuid.uuid4())[:8],
                severity="high",
                title="Low extraction confidence",
                message="Re-run OCR or verify layout detection before exporting",
                action="rerun_ocr",
            )
        )

    if parse_result and not parse_result.summary.validation_passed:
        suggestions.append(
            SmartSuggestion(
                id=str(uuid.uuid4())[:8],
                severity="high",
                title="Balance validation failed",
                message="Recalculate running balances or fix misaligned rows",
                action="recalculate",
            )
        )

    if confidence.overall >= 0.85 and (not parse_result or parse_result.summary.validation_passed):
        suggestions.append(
            SmartSuggestion(
                id=str(uuid.uuid4())[:8],
                severity="low",
                title="Export ready",
                message="Statement passes AI confidence and validation checks",
                action="export",
            )
        )

    return suggestions[:25]
