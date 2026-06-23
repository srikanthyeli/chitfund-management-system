import asyncpg
from uuid import UUID
from typing import Optional
from src.shared.core.repository.user_repository import UserRepository
from src.shared.common.helpers.password_helper import verify_password
from src.shared.common.helpers.jwt_helper import (
    create_access_token,
    create_refresh_token,
    verify_token,
    ACCESS_TOKEN_EXPIRY
)
from src.shared.common.exceptions import AuthenticationError, AuthorizationError, UserNotFoundError
from src.shared.common.logging.log import get_logger
from src.api.schemas.auth_schema import LoginRequest, RefreshTokenRequest
from src.api.models.models import User

logger = get_logger(__name__)

class AuthService:
    def __init__(self, db_object: asyncpg.Connection):
        self.user_repo = UserRepository(db_object)

    async def authenticate_user(self, mobile: str, password: str) -> User:
        """
        Validates mobile number and password, along with active and role checks.
        """
        user = await self.user_repo.get_user_by_mobile(mobile)
        if not user:
            logger.warning(f"Login failed: User with mobile {mobile} not found")
            raise AuthenticationError("Invalid mobile number or password")

        # Verify password
        if not verify_password(password, user.password_hash):
            logger.warning(f"Login failed: Invalid password for mobile {mobile}")
            raise AuthenticationError("Invalid mobile number or password")

        # Verify active state
        if not user.is_active:
            logger.warning(f"Login failed: User {user.id} is inactive")
            raise AuthenticationError("User account is disabled")

        # Verify role allowed in MVP
        # ADMIN and ORGANIZER are allowed. MEMBER login will be implemented later.
        if user.role not in ("ADMIN", "ORGANIZER"):
            logger.warning(f"Login failed: User {user.id} with role {user.role} tried to login, which is not supported in MVP")
            raise AuthorizationError("Login is currently restricted to Admin and Organizers")

        return user

    async def login(self, login_data: LoginRequest) -> dict:
        """
        Processes login request: authenticates, updates last login, and issues tokens.
        """
        user = await self.authenticate_user(login_data.mobile, login_data.password)
        
        # Update last login time
        await self.user_repo.update_last_login(user.id)
        
        # Create tokens
        token_payload = {
            "sub": str(user.id),
            "role": user.role
        }
        
        access_token = create_access_token(token_payload)
        refresh_token = create_refresh_token(token_payload)
        
        logger.info(f"Login success: User {user.id} ({user.role}) logged in successfully")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": ACCESS_TOKEN_EXPIRY * 60,
            "user": {
                "id": user.id,
                "mobile": user.mobile,
                "role": user.role
            }
        }

    async def refresh_access_token(self, refresh_data: RefreshTokenRequest) -> dict:
        """
        Validates refresh token and issues a new access token.
        """
        try:
            payload = verify_token(refresh_data.refresh_token, token_type="refresh")
        except AuthenticationError as e:
            logger.warning(f"Token refresh failed: {e.message}")
            raise

        user_id_str = payload.get("sub")
        if not user_id_str:
            logger.warning("Token refresh failed: Missing 'sub' claim in refresh token")
            raise AuthenticationError("Invalid refresh token")

        try:
            user_id = UUID(user_id_str)
        except ValueError:
            logger.warning(f"Token refresh failed: Invalid UUID 'sub' format: {user_id_str}")
            raise AuthenticationError("Invalid refresh token")

        user = await self.user_repo.get_user_by_id(user_id)
        if not user:
            logger.warning(f"Token refresh failed: User {user_id} not found")
            raise UserNotFoundError("User not found")

        if not user.is_active:
            logger.warning(f"Token refresh failed: User {user_id} is inactive")
            raise AuthenticationError("User account is disabled")

        if user.role not in ("ADMIN", "ORGANIZER"):
            logger.warning(f"Token refresh failed: Role {user.role} not allowed login")
            raise AuthorizationError("Access is currently restricted to Admin and Organizers")

        # Create new access token
        token_payload = {
            "sub": str(user.id),
            "role": user.role
        }
        
        new_access_token = create_access_token(token_payload)
        new_refresh_token = create_refresh_token(token_payload)

        logger.info(f"Token refresh success: Issued new access token for user {user.id}")

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "Bearer",
            "expires_in": ACCESS_TOKEN_EXPIRY * 60,
            "user": {
                "id": user.id,
                "mobile": user.mobile,
                "role": user.role
            }
        }

    async def get_current_user(self, token: str) -> User:
        """
        Decodes access token and retrieves corresponding active user.
        """
        try:
            payload = verify_token(token, token_type="access")
        except AuthenticationError as e:
            logger.warning(f"User validation failed: {e.message}")
            raise

        user_id_str = payload.get("sub")
        if not user_id_str:
            raise AuthenticationError("Invalid access token")

        try:
            user_id = UUID(user_id_str)
        except ValueError:
            raise AuthenticationError("Invalid access token")

        user = await self.user_repo.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError("User not found")

        if not user.is_active:
            raise AuthenticationError("User account is disabled")

        return user
