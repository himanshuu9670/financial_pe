"""User registration, login, token refresh."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit import AuditService
from app.auth.jwt_handler import create_access_token, create_refresh_token, verify_refresh_token
from app.auth.password_manager import hash_password, verify_password
from app.auth.permissions import Role
from app.auth.session_manager import revoke_refresh_token, store_refresh_token
from app.models import User

DEMO_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.audit = AuditService(db)

    def register(
        self,
        email: str,
        password: str,
        full_name: str | None = None,
        *,
        role: str = Role.EDITOR.value,
        request: Request | None = None,
    ) -> tuple[User, str, str]:
        email = email.strip().lower()
        if self.db.scalar(select(User).where(User.email == email)):
            raise HTTPException(status_code=400, detail="Email already registered")

        user = User(
            email=email,
            full_name=full_name,
            hashed_password=hash_password(password),
            role=role if role in {r.value for r in Role} else Role.EDITOR.value,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        access, refresh, jti = self._issue_tokens(user)
        self.audit.log("auth.register", user_id=user.id, status="success", request=request)
        self.db.commit()
        return user, access, refresh

    def login(
        self,
        email: str,
        password: str,
        *,
        request: Request | None = None,
    ) -> tuple[User, str, str]:
        email = email.strip().lower()
        user = self.db.scalar(select(User).where(User.email == email))
        if not user or not verify_password(password, user.hashed_password):
            self.audit.log(
                "auth.login_failed",
                status="failure",
                message=email,
                request=request,
            )
            self.db.commit()
            raise HTTPException(status_code=401, detail="Invalid email or password")

        if not user.is_active:
            raise HTTPException(status_code=403, detail="Account disabled")

        access, refresh, jti = self._issue_tokens(user)
        self.audit.log("auth.login", user_id=user.id, status="success", request=request)
        self.db.commit()
        return user, access, refresh

    def refresh(self, refresh_token: str, *, request: Request | None = None) -> tuple[str, str]:
        payload = verify_refresh_token(refresh_token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        user = self.db.get(User, uuid.UUID(payload["sub"]))
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="User not found")

        access, new_refresh, jti = self._issue_tokens(user)
        self.audit.log("auth.refresh", user_id=user.id, request=request)
        self.db.commit()
        return access, new_refresh

    def logout(self, user: User, *, jti: str | None = None, request: Request | None = None) -> None:
        if jti:
            revoke_refresh_token(jti)
        self.audit.log("auth.logout", user_id=user.id, request=request)
        self.db.commit()

    def _issue_tokens(self, user: User) -> tuple[str, str, str]:
        jti = str(uuid.uuid4())
        access = create_access_token(user.id, user.email, user.role)
        refresh = create_refresh_token(user.id)
        store_refresh_token(jti, user.id, refresh)
        return access, refresh, jti
