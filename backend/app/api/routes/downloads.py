from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.services.secure_download import SecureDownloadService
from app.core.config import get_settings

router = APIRouter(prefix="/downloads", tags=["downloads"])


@router.get("/secure/{token}")
def secure_download(token: str) -> FileResponse:
    secure = SecureDownloadService()
    payload = secure.verify_download_token(token)
    if not payload:
        raise HTTPException(status_code=403, detail="Invalid or expired download token")

    settings = get_settings()
    stmt_id = payload["stmt"]
    kind = payload.get("kind", "export")
    job_id = payload.get("job")

    if kind == "export" and job_id:
        path = settings.storage_exports / stmt_id / f"{job_id}.pdf"
    elif kind == "edited":
        path = settings.storage_edited / f"{stmt_id}.pdf"
    else:
        path = settings.storage_original / f"{stmt_id}.pdf"

    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        Path(path),
        media_type="application/pdf",
        filename=path.name,
        headers={"Cache-Control": "private, no-store"},
    )
