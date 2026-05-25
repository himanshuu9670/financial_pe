from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class SnapshotSchema(BaseModel):
    id: UUID
    statement_id: UUID
    version_number: int
    snapshot_type: str
    file_path: str
    checksum_sha256: str | None
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class SnapshotListResponse(BaseModel):
    snapshots: list[SnapshotSchema]
    total: int
