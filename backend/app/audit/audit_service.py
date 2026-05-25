"""Enterprise audit logging for all critical actions."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import Request
from sqlalchemy.orm import Session

from app.models import AuditLog
from app.utils.logging import get_logger

logger = get_logger(__name__)


class AuditService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def log(
        self,
        action: str,
        *,
        user_id: uuid.UUID | None = None,
        statement_id: uuid.UUID | None = None,
        resource_type: str = "statement",
        resource_id: str | None = None,
        status: str = "success",
        message: str | None = None,
        details: dict[str, Any] | None = None,
        request: Request | None = None,
    ) -> AuditLog:
        ip = None
        ua = None
        if request:
            ip = request.client.host if request.client else None
            ua = request.headers.get("user-agent", "")[:512]

        entry = AuditLog(
            user_id=user_id,
            statement_id=statement_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            status=status,
            message=message,
            details=details,
            ip_address=ip,
            user_agent=ua,
        )
        self.db.add(entry)
        self.db.flush()
        logger.info(
            "audit_log",
            action=action,
            user_id=str(user_id) if user_id else None,
            statement_id=str(statement_id) if statement_id else None,
            status=status,
        )
        return entry
