import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.auth.dependencies import get_current_user, require_role_dep
from app.auth.permissions import Role
from app.models import User
from app.schemas.versioning import SnapshotListResponse, SnapshotSchema
from app.services.statement_service import StatementService
from app.services.version_service import VersionService

router = APIRouter(prefix="/versions", tags=["versions"])


@router.get("/statement/{statement_id}", response_model=SnapshotListResponse)
def list_versions(
    statement_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> SnapshotListResponse:
    snaps = VersionService(db).list_snapshots(statement_id)
    return SnapshotListResponse(
        snapshots=[SnapshotSchema.model_validate(s) for s in snaps],
        total=len(snaps),
    )


@router.get("/{snapshot_id}/download")
def download_snapshot(
    snapshot_id: uuid.UUID,
    user: User = Depends(require_role_dep(Role.EDITOR)),
    db: Session = Depends(get_db_session),
) -> FileResponse:
    snap = VersionService(db).get_snapshot(snapshot_id)
    if not snap:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    path = Path(snap.file_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Snapshot file missing")
    return FileResponse(path, media_type="application/pdf", filename=path.name)
