import asyncpg
import uuid
from fastapi import APIRouter, Depends, Request
from src.api.schemas.auth_schema import (
    LoginRequest, ForceLoginRequest, RefreshTokenRequest, 
    LoginResponse, LogoutResponse, CurrentUserResponse
)
from src.shared.core.services.auth_service import AuthService
from src.shared.core.database import get_db_session
from src.api.dependencies.auth_dependency import get_current_user
from src.api.models.models import User
from src.shared.common.helpers.jwt_helper import decode_token

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/login", response_model=LoginResponse)
async def login(
    request_data: LoginRequest,
    db: asyncpg.Connection = Depends(get_db_session)
):
    service = AuthService(db)
    return await service.login(request_data)

@router.post("/force-login", response_model=LoginResponse)
async def force_login(
    request_data: ForceLoginRequest,
    db: asyncpg.Connection = Depends(get_db_session)
):
    service = AuthService(db)
    return await service.force_login(request_data)

@router.post("/refresh")
async def refresh_token(
    request_data: RefreshTokenRequest,
    db: asyncpg.Connection = Depends(get_db_session)
):
    service = AuthService(db)
    return await service.refresh_token(request_data)

@router.post("/logout", response_model=LogoutResponse)
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session)
):
    service = AuthService(db)
    auth_header = request.headers.get("Authorization")
    token = auth_header.split(" ")[1]
    payload = decode_token(token)
    session_id = payload.get("session_id")
    
    return await service.logout(current_user.id, uuid.UUID(session_id))

@router.get("/me", response_model=CurrentUserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session)
):
    service = AuthService(db)
    return await service.get_me(current_user)

@router.get("/health")
async def health_check():
    return {"status": "healthy"}
