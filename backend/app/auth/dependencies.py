"""FastAPI auth dependencies."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.auth.jwt_handler import verify_access_token
from app.auth.password_manager import hash_password
from app.auth.permissions import Role, require_role
from app.core.config import get_settings
from app.models import User

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user_optional(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Session = Depends(get_db_session),
) -> User | None:
    settings = get_settings()
    if settings.auth_disabled:
        return _demo_user(db)
    if not creds:
        return None
    payload = verify_access_token(creds.credentials)
    if not payload:
        return None
    user = db.get(User, uuid.UUID(payload["sub"]))
    if user and user.is_active:
        return user
    return None


async def get_current_user(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Session = Depends(get_db_session),
) -> User:
    settings = get_settings()
    if settings.auth_disabled:
        user = _demo_user(db)
        if user:
            return user
    if not creds:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = verify_access_token(creds.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    user = db.get(User, uuid.UUID(payload["sub"]))
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User inactive")
    return user


def require_role_dep(required: Role):
    async def _checker(user: User = Depends(get_current_user)) -> User:
        if user.is_superuser:
            return user
        require_role(user.role, required)
        return user

    return _checker


def _demo_user(db: Session) -> User | None:
    from app.services.statement_service import DEMO_USER_ID

    user = db.get(User, DEMO_USER_ID)
    if user:
        return user

    demo = User(
        id=DEMO_USER_ID,
        email="demo@local",
        full_name="Demo User",
        hashed_password=hash_password("demo-password"),
        is_active=True,
        is_superuser=False,
        role="editor",
    )
    db.add(demo)
    db.commit()
    db.refresh(demo)
    return demo
