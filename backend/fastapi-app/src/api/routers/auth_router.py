import asyncpg
from fastapi import APIRouter, Depends, status
from src.shared.core.database import get_db_session
from src.api.controllers.auth_controller import AuthController
from src.api.schemas.auth_schema import LoginRequest, LoginResponse, RefreshTokenRequest, CurrentUserResponse
from src.api.dependencies.auth_dependency import get_current_user
from src.api.models.models import User

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(login_request: LoginRequest, db_object: asyncpg.Connection = Depends(get_db_session)):
    """
    User login endpoint. Accepts mobile and password. Returns access and refresh tokens.
    """
    controller = AuthController(db_object)
    return await controller.login(login_request)

@router.post("/refresh", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def refresh_token(refresh_request: RefreshTokenRequest, db_object: asyncpg.Connection = Depends(get_db_session)):
    """
    Refresh JWT tokens using a valid refresh token.
    """
    controller = AuthController(db_object)
    return await controller.refresh_token(refresh_request)

@router.get("/me", response_model=CurrentUserResponse, status_code=status.HTTP_200_OK)
async def me(current_user: User = Depends(get_current_user)):
    """
    Get profile information of the currently authenticated user.
    """
    return {
        "id": current_user.id,
        "mobile": current_user.mobile,
        "role": current_user.role,
        "is_active": current_user.is_active
    }

@router.get("/health", status_code=status.HTTP_200_OK)
async def auth_health():
    """
    Endpoint verifying the status of the Authentication Module.
    """
    return {
        "status": "healthy",
        "service": "auth_module"
    }
