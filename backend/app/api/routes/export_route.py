import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.core.config import get_settings
from app.schemas.export import ApplyEditsRequest, ApplyEditsResponse, VisualValidationSchema
from app.schemas.statement import ExportResponse
from app.services.pdf_export_service import PdfExportService
from app.services.statement_service import StatementService
from app.utils.logging import get_logger

router = APIRouter(prefix="/export", tags=["export"])
logger = get_logger(__name__)


@router.post("/apply-edits", response_model=ApplyEditsResponse)
def apply_edits(
    payload: ApplyEditsRequest,
    db: Session = Depends(get_db_session),
) -> ApplyEditsResponse:
    """
    Apply invisible typography-preserving edits and export final PDF.
    Does not modify original — writes to storage/edited_pdfs/.
    """
    service = PdfExportService(db)

    try:
        result, statement = service.apply_edits(payload.statement_id, payload.session_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("apply_edits_failed", error=str(exc))
        raise HTTPException(status_code=422, detail=f"Export failed: {exc}") from exc

    sid = payload.statement_id
    prefix = get_settings().api_v1_prefix

    return ApplyEditsResponse(
        statement_id=sid,
        status="exported",
        download_url=f"{prefix}/preview/{sid}/edited",
        original_preview_url=f"{prefix}/preview/{sid}",
        edited_preview_url=f"{prefix}/preview/{sid}/edited",
        replacements_applied=result.replacements_applied,
        replacements_failed=result.replacements_failed,
        validation=VisualValidationSchema(
            text_match_ratio=result.validation.text_match_ratio,
            bbox_overlap_ratio=result.validation.bbox_overlap_ratio,
            regions_checked=result.validation.regions_checked,
            issues=result.validation.issues,
            passed=result.validation.passed,
        ),
        warnings=result.warnings,
    )


@router.post("/{statement_id}", response_model=ExportResponse)
def export_statement_legacy(
    statement_id: uuid.UUID,
    db: Session = Depends(get_db_session),
) -> ExportResponse:
    """Legacy export — delegates to apply-edits without session."""
    req = ApplyEditsRequest(statement_id=statement_id)
    res = apply_edits(req, db)
    return ExportResponse(
        statement_id=statement_id,
        download_url=res.download_url,
        status=res.status,
        message=f"Applied {res.replacements_applied} replacement(s).",
    )
