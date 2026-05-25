"""AI financial intelligence domain models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CategoryResult(BaseModel):
    transaction_id: str
    description: str
    category: str
    confidence: float
    signals: list[str] = Field(default_factory=list)


class AnomalyFlag(BaseModel):
    transaction_id: str
    anomaly_type: str
    severity: str  # low, medium, high
    message: str
    score: float
    details: dict = Field(default_factory=dict)


class FraudAssessment(BaseModel):
    risk_score: float
    risk_level: str  # low, medium, high, critical
    flags: list[str] = Field(default_factory=list)
    anomaly_count: int = 0


class SmartCorrection(BaseModel):
    transaction_id: str | None = None
    field: str
    original: str
    corrected: str
    confidence: float
    reason: str


class SmartSuggestion(BaseModel):
    id: str
    severity: str
    title: str
    message: str
    action: str | None = None
    transaction_id: str | None = None


class ConfidenceBreakdown(BaseModel):
    overall: float
    ocr: float | None = None
    layout: float | None = None
    financial: float | None = None
    semantic: float | None = None
    factors: list[str] = Field(default_factory=list)


class CategorySpend(BaseModel):
    category: str
    total_debit: float
    total_credit: float
    count: int
    percent_of_debit: float


class SpendingInsight(BaseModel):
    top_category: str | None = None
    largest_debit: float | None = None
    avg_debit: float | None = None
    recurring_merchants: list[str] = Field(default_factory=list)


class AiIntelligenceReport(BaseModel):
    statement_id: str
    categories: list[CategoryResult] = Field(default_factory=list)
    anomalies: list[AnomalyFlag] = Field(default_factory=list)
    fraud: FraudAssessment = Field(default_factory=lambda: FraudAssessment(risk_score=0, risk_level="low"))
    corrections: list[SmartCorrection] = Field(default_factory=list)
    suggestions: list[SmartSuggestion] = Field(default_factory=list)
    confidence: ConfidenceBreakdown = Field(default_factory=lambda: ConfidenceBreakdown(overall=0))
    category_spend: list[CategorySpend] = Field(default_factory=list)
    spending_insight: SpendingInsight = Field(default_factory=SpendingInsight)
    semantic_index_size: int = 0
    cached: bool = False
