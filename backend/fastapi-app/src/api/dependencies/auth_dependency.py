import asyncpg
from uuid import UUID
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.shared.core.database import get_db_session
from src.shared.core.repository.user_repository import UserRepository
from src.shared.core.repository.organizer_repository import OrganizerRepository
from src.shared.core.repository.user_session_repository import UserSessionRepository
from src.shared.common.helpers.jwt_helper import decode_token
from src.api.models.models import User

security_scheme = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db_object: asyncpg.Connection = Depends(get_db_session)
) -> User:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = credentials.credentials
    try:
        payload = decode_token(token)
        if payload.get("token_type") != "access":
            raise ValueError("Invalid token type")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    session_id = payload.get("session_id")
    user_id = payload.get("user_id")

    session_repo = UserSessionRepository(db_object)
    session = await session_repo.get_session_by_id(UUID(session_id))
    if not session or not session.is_active:
        raise HTTPException(status_code=401, detail="Session expired or inactive")

    user_repo = UserRepository(db_object)
    user = await user_repo.get_user_by_id(UUID(user_id))
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User account disabled")

    if user.role == "ORGANIZER" and user.organizer_id:
        org_repo = OrganizerRepository(db_object)
        org = await org_repo.get_organizer_by_id(user.organizer_id)
        if not org or not org.is_active:
            raise HTTPException(status_code=403, detail="Organizer account is disabled")

    return user

async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin role required")
    return current_user

async def get_current_organizer(
    current_user: User = Depends(get_current_user)
) -> User:
    if current_user.role != "ORGANIZER":
        raise HTTPException(status_code=403, detail="Organizer role required")
    return current_user

async def get_current_member(
    current_user: User = Depends(get_current_user)
) -> User:
    if current_user.role != "MEMBER":
        raise HTTPException(status_code=403, detail="Member role required")
    if not current_user.member_id:
        raise HTTPException(status_code=403, detail="No member profile linked to this user")
    return current_user
