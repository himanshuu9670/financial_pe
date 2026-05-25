"""JWT access and refresh token creation / validation."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from jose import JWTError, jwt

from app.core.config import get_settings


def _settings():
    return get_settings()


def create_access_token(
    user_id: UUID,
    email: str,
    role: str,
    *,
    extra: dict[str, Any] | None = None,
) -> str:
    s = _settings()
    expire = datetime.now(timezone.utc) + timedelta(minutes=s.jwt_access_expire_minutes)
    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "type": "access",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, s.jwt_secret_key, algorithm=s.jwt_algorithm)


def create_refresh_token(user_id: UUID) -> str:
    s = _settings()
    expire = datetime.now(timezone.utc) + timedelta(days=s.jwt_refresh_expire_days)
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, s.jwt_secret_key, algorithm=s.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    s = _settings()
    return jwt.decode(token, s.jwt_secret_key, algorithms=[s.jwt_algorithm])


def verify_access_token(token: str) -> dict[str, Any] | None:
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError:
        return None


def verify_refresh_token(token: str) -> dict[str, Any] | None:
    try:
        payload = decode_token(token)
        if payload.get("type") != "refresh":
            return None
        return payload
    except JWTError:
        return None
