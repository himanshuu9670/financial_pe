"""Refresh token persistence (Redis + optional DB revocation set)."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from app.core.config import get_settings
from app.core.database.redis_client import get_redis
from app.utils.logging import get_logger

logger = get_logger(__name__)

REFRESH_PREFIX = "refresh_token:"


def store_refresh_token(jti: str, user_id: uuid.UUID, token: str) -> None:
    s = get_settings()
    key = f"{REFRESH_PREFIX}{jti}"
    payload = {
        "user_id": str(user_id),
        "token": token,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    ttl = s.jwt_refresh_expire_days * 86400
    try:
        redis = get_redis()
        redis.setex(key, ttl, json.dumps(payload))
    except Exception as exc:
        logger.warning("refresh_token_store_failed", error=str(exc))


def revoke_refresh_token(jti: str) -> None:
    try:
        redis = get_redis()
        redis.delete(f"{REFRESH_PREFIX}{jti}")
    except Exception as exc:
        logger.warning("refresh_token_revoke_failed", error=str(exc))


def get_refresh_session(jti: str) -> dict | None:
    try:
        redis = get_redis()
        raw = redis.get(f"{REFRESH_PREFIX}{jti}")
        if raw:
            return json.loads(raw)
    except Exception as exc:
        logger.warning("refresh_token_get_failed", error=str(exc))
    return None
