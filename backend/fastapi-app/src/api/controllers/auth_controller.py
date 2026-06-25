import asyncpg
from src.shared.core.services.auth_service import AuthService
from src.api.schemas.auth_schema import LoginRequest, RefreshTokenRequest
from src.api.models.models import User

class AuthController:
    def __init__(self, db_object: asyncpg.Connection):
        self.db_object = db_object
        self.auth_service = AuthService(db_object)

    async def login(self, login_request: LoginRequest) -> dict:
        """
        Handles user login request.
        """
        return await self.auth_service.login(login_request)

    async def refresh_token(self, refresh_request: RefreshTokenRequest) -> dict:
        """
        Handles token refresh request.
        """
        return await self.auth_service.refresh_access_token(refresh_request)

    async def me(self, current_user: User) -> dict:
        """
        Handles current user details request.
        """
        return {
            "id": current_user.id,
            "mobile": current_user.mobile,
            "role": current_user.role,
            "is_active": current_user.is_active
        }
