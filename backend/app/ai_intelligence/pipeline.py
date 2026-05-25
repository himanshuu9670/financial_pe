"""AI processing pipeline: parse → semantic → categorize → detect → score → insights."""

from __future__ import annotations

from app.shared.models import StructuredTransaction
from app.ai_engine.models import TransactionParseResult
from app.ai_intelligence.anomaly_detector import detect_anomalies
from app.ai_intelligence.categorizer import categorize_transactions
from app.ai_intelligence.confidence_booster import boost_confidence
from app.ai_intelligence.embeddings_engine import EmbeddingsIndex
from app.ai_intelligence.exceptions import AiNoTransactionsError
from app.ai_intelligence.fraud_engine import assess_fraud
from app.ai_intelligence.models import AiIntelligenceReport
from app.ai_intelligence.pattern_engine import analyze_spending
from app.ai_intelligence.smart_corrector import suggest_corrections
from app.ai_intelligence.suggestion_engine import build_suggestions


def run_ai_pipeline(
    statement_id: str,
    transactions: list[StructuredTransaction],
    parse_result: TransactionParseResult | None = None,
    *,
    ocr_confidence: float | None = None,
    layout_confidence: float | None = None,
    embeddings_index: EmbeddingsIndex | None = None,
) -> AiIntelligenceReport:
    if not transactions:
        raise AiNoTransactionsError(
            "No transactions available — parse the statement before running AI analysis"
        )

    index = embeddings_index or EmbeddingsIndex(transactions)
    categories = categorize_transactions(transactions)
    anomalies = detect_anomalies(transactions, embeddings_index=index)
    fraud = assess_fraud(transactions, anomalies)
    corrections = suggest_corrections(transactions)
    confidence = boost_confidence(
        parse_result,
        categories,
        transactions,
        ocr_confidence=ocr_confidence,
        layout_confidence=layout_confidence,
    )
    category_spend, spending_insight = analyze_spending(categories, transactions)
    suggestions = build_suggestions(
        parse_result=parse_result,
        anomalies=anomalies,
        corrections=corrections,
        confidence=confidence,
    )
    return AiIntelligenceReport(
        statement_id=statement_id,
        categories=categories,
        anomalies=anomalies,
        fraud=fraud,
        corrections=corrections,
        suggestions=suggestions,
        confidence=confidence,
        category_spend=category_spend,
        spending_insight=spending_insight,
        semantic_index_size=len(index.entries),
        cached=False,
    )
