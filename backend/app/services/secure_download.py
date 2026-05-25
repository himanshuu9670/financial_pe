"""Signed temporary download tokens for PDF files."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.core.config import get_settings


class SecureDownloadService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def token_ttl_delta(self) -> timedelta:
        return timedelta(minutes=self.settings.secure_download_expire_minutes)

    def create_download_token(
        self,
        *,
        statement_id: uuid.UUID,
        path_kind: str,
        job_id: uuid.UUID | None = None,
    ) -> str:
        expire = datetime.now(timezone.utc) + self.token_ttl_delta()
        payload = {
            "stmt": str(statement_id),
            "kind": path_kind,
            "job": str(job_id) if job_id else None,
            "exp": expire,
            "type": "download",
        }
        return jwt.encode(
            payload,
            self.settings.jwt_secret_key,
            algorithm=self.settings.jwt_algorithm,
        )

    def verify_download_token(self, token: str) -> dict | None:
        try:
            payload = jwt.decode(
                token,
                self.settings.jwt_secret_key,
                algorithms=[self.settings.jwt_algorithm],
            )
            if payload.get("type") != "download":
                return None
            return payload
        except JWTError:
            return None
