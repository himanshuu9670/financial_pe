from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.pdf_engine.exceptions import PdfEncryptedError, PdfEngineError, PdfValidationError
from app.schemas.statement import UploadResponse
from app.services.statement_service import StatementService
from app.utils.logging import get_logger

router = APIRouter(prefix="/upload", tags=["upload"])
logger = get_logger(__name__)


@router.post("", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_statement(
    file: UploadFile = File(...),
    db: Session = Depends(get_db_session),
) -> UploadResponse:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    service = StatementService(db)

    try:
        statement = await service.create_from_upload(file)
    except PdfEncryptedError:
        raise HTTPException(
            status_code=400,
            detail="PDF is password-protected. Please upload an unencrypted statement.",
        )
    except PdfValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except PdfEngineError as exc:
        logger.warning("pdf_engine_error", error=str(exc))
        raise HTTPException(status_code=422, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.error("upload_unexpected", error=str(exc))
        raise HTTPException(status_code=500, detail="Upload failed")

    return UploadResponse(
        statement_id=statement.id,
        filename=statement.original_filename,
        status=statement.status,
        message="PDF uploaded successfully",
        file_size_bytes=statement.file_size_bytes,
        page_count=statement.page_count,
        storage_path=statement.original_pdf_path,
    )
