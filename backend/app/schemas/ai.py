"""API schemas for AI financial intelligence."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CategoryItemSchema(BaseModel):
    transaction_id: str
    description: str
    category: str
    confidence: float
    signals: list[str] = Field(default_factory=list)


class AnomalyItemSchema(BaseModel):
    transaction_id: str
    anomaly_type: str
    severity: str
    message: str
    score: float
    details: dict = Field(default_factory=dict)


class FraudSchema(BaseModel):
    risk_score: float
    risk_level: str
    flags: list[str] = Field(default_factory=list)
    anomaly_count: int = 0


class CorrectionSchema(BaseModel):
    transaction_id: str | None = None
    field: str
    original: str
    corrected: str
    confidence: float
    reason: str


class SuggestionSchema(BaseModel):
    id: str
    severity: str
    title: str
    message: str
    action: str | None = None
    transaction_id: str | None = None


class ConfidenceSchema(BaseModel):
    overall: float
    ocr: float | None = None
    layout: float | None = None
    financial: float | None = None
    semantic: float | None = None
    factors: list[str] = Field(default_factory=list)


class CategorySpendSchema(BaseModel):
    category: str
    total_debit: float
    total_credit: float
    count: int
    percent_of_debit: float


class AiInsightsResponse(BaseModel):
    statement_id: str
    cached: bool = False
    confidence: ConfidenceSchema
    fraud: FraudSchema
    category_spend: list[CategorySpendSchema] = Field(default_factory=list)
    spending_insight: dict = Field(default_factory=dict)
    anomaly_count: int = 0
    suggestion_count: int = 0
    top_category: str | None = None


class AiCategoriesResponse(BaseModel):
    statement_id: str
    categories: list[CategoryItemSchema]
    cached: bool = False


class AiAnomaliesResponse(BaseModel):
    statement_id: str
    anomalies: list[AnomalyItemSchema]
    fraud: FraudSchema
    cached: bool = False


class AiConfidenceResponse(BaseModel):
    statement_id: str
    confidence: ConfidenceSchema
    corrections: list[CorrectionSchema] = Field(default_factory=list)
    cached: bool = False


class AiSuggestionsRequest(BaseModel):
    statement_id: str | None = None
    query: str | None = None


class AiSuggestionsResponse(BaseModel):
    statement_id: str
    suggestions: list[SuggestionSchema]
    corrections: list[CorrectionSchema] = Field(default_factory=list)
    cached: bool = False


class SemanticSearchResponse(BaseModel):
    statement_id: str
    query: str
    results: list[dict]
