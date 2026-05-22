from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    message: str
    detail: str | None = None


class HealthResponse(BaseModel):
    status: str
    app: str
    database: bool
    redis: bool
    timestamp: datetime
