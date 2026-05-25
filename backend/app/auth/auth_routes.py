from uuid import UUID

from fastapi import APIRouter, Depends, Request

from app.api.middleware.rate_limit import limiter
from app.core.config import get_settings
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.auth.dependencies import get_current_user
from app.auth.password_manager import hash_password
from app.models import User
from app.schemas.auth import (
    LoginRequest,
    ProfileUpdateRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
def register(
    payload: RegisterRequest,
    request: Request,
    db: Session = Depends(get_db_session),
) -> TokenResponse:
    service = AuthService(db)
    _, access, refresh = service.register(
        payload.email,
        payload.password,
        payload.full_name,
        request=request,
    )
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/login", response_model=TokenResponse)
@limiter.limit(lambda: get_settings().rate_limit_auth)
def login(
    request: Request,
    payload: LoginRequest,
    db: Session = Depends(get_db_session),
) -> TokenResponse:
    service = AuthService(db)
    _, access, refresh = service.login(payload.email, payload.password, request=request)
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    payload: RefreshRequest,
    request: Request,
    db: Session = Depends(get_db_session),
) -> TokenResponse:
    service = AuthService(db)
    access, new_refresh = service.refresh(payload.refresh_token, request=request)
    return TokenResponse(access_token=access, refresh_token=new_refresh)


@router.post("/logout")
def logout(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> dict:
    AuthService(db).logout(user, request=request)
    return {"message": "Logged out"}


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)) -> User:
    return user


@router.patch("/me", response_model=UserResponse)
def update_profile(
    payload: ProfileUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> User:
    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.password:
        user.hashed_password = hash_password(payload.password)
    db.commit()
    db.refresh(user)
    return user
