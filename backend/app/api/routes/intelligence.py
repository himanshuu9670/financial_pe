import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.schemas.intelligence import (
    BankSignatureSchema,
    ColumnSchema,
    IntelligenceAnalysisResponse,
    LayoutAnalysisSchema,
    RowSegmentSchema,
    TableRegionSchema,
)
from app.services.intelligence_service import IntelligenceService
from app.services.statement_service import StatementService
from app.utils.logging import get_logger

router = APIRouter(tags=["intelligence"])
logger = get_logger(__name__)


@router.get(
    "/statements/{statement_id}/intelligence",
    response_model=IntelligenceAnalysisResponse,
)
def get_statement_intelligence(
    statement_id: uuid.UUID,
    refresh: bool = Query(default=False),
    force_ocr: bool = Query(default=False),
    db: Session = Depends(get_db_session),
) -> IntelligenceAnalysisResponse:
    stmt_service = StatementService(db)
    statement = stmt_service.get_by_id(statement_id)
    if not statement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Statement not found")

    intel_service = IntelligenceService(db)
    try:
        layout, parse_result, debug, cached = intel_service.analyze(
            statement_id,
            force_refresh=refresh,
            force_ocr=force_ocr,
            include_debug=True,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("intelligence_failed", statement_id=str(statement_id), error=str(exc))
        raise HTTPException(status_code=422, detail=f"Intelligence analysis failed: {exc}") from exc

    row_segments = []
    if debug:
        row_segments = [
            RowSegmentSchema(
                page=s.page,
                row_index=s.row_index,
                bbox=s.bbox,
                text=s.text[:200],
                span_count=s.span_count,
                confidence=s.confidence,
            )
            for s in debug.row_segments[:80]
        ]

    return IntelligenceAnalysisResponse(
        statement_id=statement_id,
        layout=LayoutAnalysisSchema(
            bank=BankSignatureSchema(
                bank=layout.bank.bank,
                confidence=layout.bank.confidence,
                layout_version=layout.bank.layout_version,
                signals=layout.bank.signals,
            ),
            extraction_mode=layout.extraction_mode.value,
            table_regions=[
                TableRegionSchema(
                    page=t.page,
                    bbox=t.bbox,
                    row_count_estimate=t.row_count_estimate,
                    confidence=t.confidence,
                )
                for t in layout.table_regions
            ],
            columns=[
                ColumnSchema(name=c.name, x_min=c.x_min, x_max=c.x_max, x_center=c.x_center)
                for c in layout.columns
            ],
            header_row_y=layout.header_row_y,
            layout_confidence=layout.layout_confidence,
            ocr_confidence=layout.ocr_confidence,
            is_scanned=layout.is_scanned,
            unknown_bank_adaptive=layout.unknown_bank_adaptive,
            warnings=layout.warnings,
        ),
        transaction_count=len(parse_result.transactions),
        layout_confidence=layout.layout_confidence,
        ocr_confidence=layout.ocr_confidence,
        extraction_mode=layout.extraction_mode.value,
        bank=layout.bank.bank,
        bank_confidence=layout.bank.confidence,
        columns=[
            ColumnSchema(name=c.name, x_min=c.x_min, x_max=c.x_max, x_center=c.x_center)
            for c in layout.columns
        ],
        table_regions=[
            TableRegionSchema(
                page=t.page,
                bbox=t.bbox,
                row_count_estimate=t.row_count_estimate,
                confidence=t.confidence,
            )
            for t in layout.table_regions
        ],
        row_segments=row_segments,
        warnings=parse_result.warnings + layout.warnings,
        cached=cached,
    )
