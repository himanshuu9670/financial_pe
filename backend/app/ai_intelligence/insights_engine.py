"""Dashboard insights aggregation."""

from __future__ import annotations

from app.ai_intelligence.models import AiIntelligenceReport


def build_dashboard_summary(report: AiIntelligenceReport) -> dict:
    high_anomalies = sum(1 for a in report.anomalies if a.severity == "high")
    return {
        "statement_id": report.statement_id,
        "overall_confidence": report.confidence.overall,
        "risk_score": report.fraud.risk_score,
        "risk_level": report.fraud.risk_level,
        "category_count": len(report.category_spend),
        "anomaly_count": len(report.anomalies),
        "high_severity_anomalies": high_anomalies,
        "suggestion_count": len(report.suggestions),
        "correction_count": len(report.corrections),
        "top_category": report.spending_insight.top_category,
        "cached": report.cached,
    }
