import asyncpg
from fastapi import APIRouter, Depends
from src.api.schemas.auth_schema import (
    LoginRequest, ForceLoginRequest, RefreshTokenRequest,
    LoginResponse, LogoutResponse, CurrentUserResponse,
    RequestOTP, SendOTPRequest, VerifyOTPRequest, TwilioOTPResponse,
    RefreshTokenResponse
)
from src.shared.core.services.auth_service import AuthService
from src.shared.core.services.twilio_service import TwilioService
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

def get_twilio_service() -> TwilioService:
    return TwilioService()


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


@router.post("/login/request-otp", status_code=200)
async def request_otp(
    request_data: RequestOTP,
    service: AuthService = Depends(get_auth_service)
):
    """
    Request OTP for login.
    """
    return await service.request_login_otp(request_data)

@router.post("/send-otp", response_model=TwilioOTPResponse, status_code=200)
async def send_otp(
    request_data: SendOTPRequest,
    service: TwilioService = Depends(get_twilio_service)
):
    """
    Send an OTP using Twilio Verify API.
    """
    import re
    from fastapi import HTTPException
    
    if not re.match(r"^\+[1-9]\d{1,14}$", request_data.phone_number):
        raise HTTPException(status_code=400, detail="Invalid phone number format. Must be E.164")
    
    return service.send_otp(request_data.phone_number)

@router.post("/verify-otp", response_model=TwilioOTPResponse, status_code=200)
async def verify_otp(
    request_data: VerifyOTPRequest,
    service: TwilioService = Depends(get_twilio_service)
):
    """
    Verify an OTP using Twilio Verify API.
    """
    import re
    from fastapi import HTTPException
    
    if not re.match(r"^\+[1-9]\d{1,14}$", request_data.phone_number):
        raise HTTPException(status_code=400, detail="Invalid phone number format. Must be E.164")
    
    response = service.verify_otp(request_data.phone_number, request_data.otp)
    
    # Send a structured 200 OK with success=False if verification fails
    # (or could raise HTTPException if preferred, but schema requires success/message)
    return TwilioOTPResponse(**response)


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
