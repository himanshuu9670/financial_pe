import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.api.middleware.rate_limit import limiter
from app.core.config import get_settings
from app.schemas.ai import (
    AiAnomaliesResponse,
    AiCategoriesResponse,
    AiConfidenceResponse,
    AiInsightsResponse,
    AiSuggestionsRequest,
    AiSuggestionsResponse,
    AnomalyItemSchema,
    CategoryItemSchema,
    CategorySpendSchema,
    ConfidenceSchema,
    CorrectionSchema,
    FraudSchema,
    SemanticSearchResponse,
    SuggestionSchema,
)
from app.ai_intelligence.exceptions import AiNoTransactionsError
from app.services.ai_intelligence_service import AiIntelligenceService
from app.services.statement_service import StatementService
from app.utils.logging import get_logger

router = APIRouter(prefix="/ai", tags=["ai"])
logger = get_logger(__name__)


def _get_report(statement_id: uuid.UUID, db: Session, refresh: bool):
    service = AiIntelligenceService(db)
    try:
        return service.analyze(statement_id, force_refresh=refresh)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except AiNoTransactionsError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.error("ai_intelligence_failed", statement_id=str(statement_id), error=str(exc))
        raise HTTPException(status_code=422, detail=f"AI analysis failed: {exc}") from exc


@router.get("/status")
def get_ai_status(
    statement_id: uuid.UUID = Query(...),
    db: Session = Depends(get_db_session),
) -> dict:
    service = AiIntelligenceService(db)
    try:
        return service.get_status(statement_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/categories", response_model=AiCategoriesResponse)
def get_ai_categories(
    statement_id: uuid.UUID = Query(..., description="Statement UUID"),
    refresh: bool = Query(default=False),
    db: Session = Depends(get_db_session),
) -> AiCategoriesResponse:
    report, cached = _get_report(statement_id, db, refresh)
    return AiCategoriesResponse(
        statement_id=str(statement_id),
        categories=[CategoryItemSchema.model_validate(c) for c in report.categories],
        cached=cached,
    )


@router.get("/anomalies", response_model=AiAnomaliesResponse)
def get_ai_anomalies(
    statement_id: uuid.UUID = Query(...),
    refresh: bool = Query(default=False),
    db: Session = Depends(get_db_session),
) -> AiAnomaliesResponse:
    report, cached = _get_report(statement_id, db, refresh)
    return AiAnomaliesResponse(
        statement_id=str(statement_id),
        anomalies=[AnomalyItemSchema.model_validate(a) for a in report.anomalies],
        fraud=FraudSchema.model_validate(report.fraud),
        cached=cached,
    )


@router.get("/insights", response_model=AiInsightsResponse)
def get_ai_insights(
    statement_id: uuid.UUID = Query(...),
    refresh: bool = Query(default=False),
    db: Session = Depends(get_db_session),
) -> AiInsightsResponse:
    report, cached = _get_report(statement_id, db, refresh)
    return AiInsightsResponse(
        statement_id=str(statement_id),
        cached=cached,
        confidence=ConfidenceSchema.model_validate(report.confidence),
        fraud=FraudSchema.model_validate(report.fraud),
        category_spend=[CategorySpendSchema.model_validate(c) for c in report.category_spend],
        spending_insight=report.spending_insight.model_dump(),
        anomaly_count=len(report.anomalies),
        suggestion_count=len(report.suggestions),
        top_category=report.spending_insight.top_category,
    )


@router.get("/confidence", response_model=AiConfidenceResponse)
def get_ai_confidence(
    statement_id: uuid.UUID = Query(...),
    refresh: bool = Query(default=False),
    db: Session = Depends(get_db_session),
) -> AiConfidenceResponse:
    report, cached = _get_report(statement_id, db, refresh)
    return AiConfidenceResponse(
        statement_id=str(statement_id),
        confidence=ConfidenceSchema.model_validate(report.confidence),
        corrections=[CorrectionSchema.model_validate(c) for c in report.corrections],
        cached=cached,
    )


@router.post("/suggestions", response_model=AiSuggestionsResponse)
def post_ai_suggestions(
    body: AiSuggestionsRequest,
    statement_id: uuid.UUID = Query(...),
    refresh: bool = Query(default=False),
    db: Session = Depends(get_db_session),
) -> AiSuggestionsResponse:
    report, cached = _get_report(statement_id, db, refresh)
    suggestions = list(report.suggestions)
    if body.query:
        service = AiIntelligenceService(db)
        hits = service.semantic_search(statement_id, body.query, limit=10)
        for hit in hits:
            suggestions.append(
                SuggestionSchema(
                    id=f"search-{hit['transaction_id'][:8]}",
                    severity="low",
                    title="Semantic match",
                    message=f"{hit['description']} ({hit['category']}, score {hit['score']})",
                    action="highlight_transaction",
                    transaction_id=hit["transaction_id"],
                )
            )
    return AiSuggestionsResponse(
        statement_id=str(statement_id),
        suggestions=suggestions[:30],
        corrections=[CorrectionSchema.model_validate(c) for c in report.corrections],
        cached=cached,
    )


@router.get("/search", response_model=SemanticSearchResponse)
@limiter.limit(lambda: get_settings().rate_limit_ai)
def semantic_search(
    request: Request,
    statement_id: uuid.UUID = Query(...),
    q: str = Query(..., min_length=2),
    limit: int = Query(default=20, ge=1, le=50),
    db: Session = Depends(get_db_session),
) -> SemanticSearchResponse:
    stmt = StatementService(db).get_by_id(statement_id)
    if not stmt:
        raise HTTPException(status_code=404, detail="Statement not found")
    service = AiIntelligenceService(db)
    try:
        results = service.semantic_search(statement_id, q, limit=limit)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except AiNoTransactionsError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("semantic_search_failed", statement_id=str(statement_id), error=str(exc))
        raise HTTPException(status_code=422, detail="Semantic search failed") from exc
    return SemanticSearchResponse(statement_id=str(statement_id), query=q, results=results)


@router.post("/analyze/{statement_id}")
@limiter.limit(lambda: get_settings().rate_limit_ai)
def trigger_ai_analysis(
    request: Request,
    statement_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    async_mode: bool = Query(default=False),
    db: Session = Depends(get_db_session),
) -> dict:
    """Run full AI pipeline (sync or Celery background)."""
    stmt = StatementService(db).get_by_id(statement_id)
    if not stmt:
        raise HTTPException(status_code=404, detail="Statement not found")

    if async_mode:
        from app.workers.tasks import run_ai_intelligence

        run_ai_intelligence.delay(str(statement_id))
        return {"statement_id": str(statement_id), "status": "queued"}

    report, cached = _get_report(statement_id, db, refresh=True)
    return {
        "statement_id": str(statement_id),
        "status": "completed",
        "cached": cached,
        "confidence": report.confidence.overall,
        "anomaly_count": len(report.anomalies),
    }
