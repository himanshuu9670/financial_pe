"""PDF versioning — immutable snapshots and rollback."""

from __future__ import annotations

import hashlib
import shutil
import uuid
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import PdfSnapshot, Statement
from app.utils.logging import get_logger

logger = get_logger(__name__)


class VersionService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()

    def create_snapshot(
        self,
        statement: Statement,
        source_path: Path,
        *,
        snapshot_type: str = "edit_commit",
        user_id: uuid.UUID | None = None,
        metadata: dict | None = None,
        notes: str | None = None,
    ) -> PdfSnapshot:
        version_num = self._next_version(statement.id)
        dest_dir = self.settings.storage_snapshots / str(statement.id)
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / f"v{version_num}_{snapshot_type}.pdf"
        shutil.copy2(source_path, dest)
        checksum = _sha256_file(dest)

        snap = PdfSnapshot(
            statement_id=statement.id,
            user_id=user_id,
            version_number=version_num,
            snapshot_type=snapshot_type,
            file_path=str(dest),
            checksum_sha256=checksum,
            metadata_json=metadata,
            notes=notes,
        )
        self.db.add(snap)
        statement.version = version_num
        self.db.flush()
        logger.info(
            "snapshot_created",
            statement_id=str(statement.id),
            version=version_num,
            type=snapshot_type,
        )
        return snap

    def list_snapshots(self, statement_id: uuid.UUID) -> list[PdfSnapshot]:
        q = (
            select(PdfSnapshot)
            .where(PdfSnapshot.statement_id == statement_id)
            .order_by(PdfSnapshot.version_number.desc())
        )
        return list(self.db.scalars(q).all())

    def get_snapshot(self, snapshot_id: uuid.UUID) -> PdfSnapshot | None:
        return self.db.get(PdfSnapshot, snapshot_id)

    def restore_snapshot(self, snapshot: PdfSnapshot) -> Path:
        path = Path(snapshot.file_path)
        if not path.exists():
            raise FileNotFoundError(f"Snapshot file missing: {path}")
        return path

    def _next_version(self, statement_id: uuid.UUID) -> int:
        current = self.db.scalar(
            select(func.max(PdfSnapshot.version_number)).where(
                PdfSnapshot.statement_id == statement_id
            )
        )
        return (current or 0) + 1


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()
