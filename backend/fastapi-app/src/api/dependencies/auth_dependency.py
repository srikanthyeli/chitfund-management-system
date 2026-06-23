import asyncpg
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from src.shared.core.database import get_db_session
from src.shared.core.services.auth_service import AuthService
from src.shared.common.exceptions import AuthenticationError, AuthorizationError
from src.api.models.models import User

security_scheme = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db_object: asyncpg.Connection = Depends(get_db_session)
) -> User:
    """
    Dependency to validate the access token and return the current authenticated user.
    """
    if not credentials or credentials.scheme.lower() != "bearer":
        raise AuthenticationError("Not authenticated")
    
    auth_service = AuthService(db_object)
    return await auth_service.get_current_user(credentials.credentials)

async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to restrict access to admin users.
    """
    if current_user.role != "ADMIN":
        raise AuthorizationError("Access denied: Admin role required")
    return current_user

async def get_current_organizer(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to restrict access to organizer users.
    """
    if current_user.role != "ORGANIZER":
        raise AuthorizationError("Access denied: Organizer role required")
    return current_user
