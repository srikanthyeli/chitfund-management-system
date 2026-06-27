import asyncpg
from fastapi import APIRouter, Depends
from src.api.schemas.auth_schema import (
    LoginRequest, ForceLoginRequest, RefreshTokenRequest,
    LoginResponse, LogoutResponse, CurrentUserResponse
)
from src.api.schemas.auth_schema import RefreshTokenResponse
from src.shared.core.services.auth_service import AuthService
from src.shared.core.database import get_db_session
from src.api.dependencies.auth_dependency import get_current_user, get_current_session_id
from src.api.models.models import User

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


# ── Service Factory ──────────────────────────────────────────────────────────
# Injected via Depends() so every endpoint is independently testable.
# To mock in tests: app.dependency_overrides[get_auth_service] = lambda: MockAuthService()

def get_auth_service(
    db: asyncpg.Connection = Depends(get_db_session)
) -> AuthService:
    return AuthService(db)


# ── Public Endpoints (no auth required) ──────────────────────────────────────

@router.post("/login", response_model=LoginResponse, status_code=200)
async def login(
    request_data: LoginRequest,
    service: AuthService = Depends(get_auth_service)
):
    """
    Authenticate a user. Returns access + refresh tokens.
    If the account is already active on another device, returns 409 FORCE_LOGIN_REQUIRED.
    """
    return await service.login(request_data)


@router.post("/force-login", response_model=LoginResponse, status_code=200)
async def force_login(
    request_data: ForceLoginRequest,
    service: AuthService = Depends(get_auth_service)
):
    """
    Forcefully log in, terminating any existing active sessions on other devices.
    """
    return await service.force_login(request_data)


@router.post("/refresh", response_model=RefreshTokenResponse, status_code=200)
async def refresh_token(
    request_data: RefreshTokenRequest,
    service: AuthService = Depends(get_auth_service)
):
    """
    Issue a new access token using a valid refresh token.
    """
    return await service.refresh_token(request_data)


# ── Protected Endpoints (Bearer token required) ───────────────────────────────

@router.post("/logout", response_model=LogoutResponse, status_code=200)
async def logout(
    current_user: User = Depends(get_current_user),
    session_id: str = Depends(get_current_session_id),
    service: AuthService = Depends(get_auth_service)
):
    """
    Invalidate the current user session.
    Session ID is extracted from the JWT by get_current_session_id dependency —
    no manual header parsing in the router.
    """
    return await service.logout(current_user.id, session_id)


@router.get("/me", response_model=CurrentUserResponse, status_code=200)
async def get_me(
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service)
):
    """
    Return the profile of the currently authenticated user.
    """
    return await service.get_me(current_user)
