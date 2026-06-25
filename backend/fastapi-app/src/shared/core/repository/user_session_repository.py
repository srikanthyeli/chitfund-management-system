from uuid import UUID
import uuid
from typing import Optional
from datetime import datetime, timezone
from src.api.models.models import UserSession

class UserSessionRepository:
    def __init__(self, db_object):
        self.db_object = db_object

    async def create_session(self, user_id: UUID, device_id: Optional[str], device_name: Optional[str], ip_address: Optional[str], refresh_token: str, access_token_expires_at: datetime, refresh_token_expires_at: datetime) -> UserSession:
        session_id = uuid.uuid4()
        now = datetime.utcnow()
        query = """
            INSERT INTO user_sessions (id, user_id, device_id, device_name, ip_address, refresh_token, login_at, access_token_expires_at, refresh_token_expires_at, last_activity_at, is_active, created_at, is_deleted, version)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, TRUE, $11, FALSE, 1)
            RETURNING id, user_id, device_id, device_name, ip_address, access_token, refresh_token, login_at, access_token_expires_at, refresh_token_expires_at, last_activity_at, logout_at, is_active
        """
        row = await self.db_object.fetchrow(
            query,
            session_id, user_id, device_id, device_name, ip_address, refresh_token,
            now, access_token_expires_at, refresh_token_expires_at, now, now
        )
        return UserSession(**dict(row))

    async def get_active_session_by_refresh_token(self, refresh_token: str) -> Optional[UserSession]:
        query = """
            SELECT id, user_id, device_id, device_name, ip_address, access_token, refresh_token, login_at, access_token_expires_at, refresh_token_expires_at, last_activity_at, logout_at, is_active
            FROM user_sessions
            WHERE refresh_token = $1 AND is_active = TRUE AND is_deleted = FALSE
        """
        row = await self.db_object.fetchrow(query, refresh_token)
        if row:
            return UserSession(**dict(row))
        return None

    async def get_active_session_by_user_id(self, user_id: UUID) -> Optional[UserSession]:
        query = """
            SELECT id, user_id, device_id, device_name, ip_address, access_token, refresh_token, login_at, access_token_expires_at, refresh_token_expires_at, last_activity_at, logout_at, is_active
            FROM user_sessions
            WHERE user_id = $1 AND is_active = TRUE AND is_deleted = FALSE
        """
        row = await self.db_object.fetchrow(query, user_id)
        if row:
            return UserSession(**dict(row))
        return None

    async def get_session_by_id(self, session_id: UUID) -> Optional[UserSession]:
        query = """
            SELECT id, user_id, device_id, device_name, ip_address, access_token, refresh_token, login_at, access_token_expires_at, refresh_token_expires_at, last_activity_at, logout_at, is_active
            FROM user_sessions
            WHERE id = $1 AND is_deleted = FALSE
        """
        row = await self.db_object.fetchrow(query, session_id)
        if row:
            return UserSession(**dict(row))
        return None

    async def deactivate_all_sessions_for_user(self, user_id: UUID) -> None:
        now = datetime.utcnow()
        query = """
            UPDATE user_sessions
            SET is_active = FALSE, logout_at = $1, updated_at = $2
            WHERE user_id = $3 AND is_active = TRUE AND is_deleted = FALSE
        """
        await self.db_object.execute(query, now, now, user_id)

    async def update_session_activity(self, session_id: UUID, access_token_expires_at: datetime) -> None:
        query = """
            UPDATE user_sessions
            SET last_activity_at = $1, access_token_expires_at = $2, updated_at = $3
            WHERE id = $4 AND is_deleted = FALSE
        """
        now = datetime.utcnow()
        await self.db_object.execute(query, now, access_token_expires_at, now, session_id)

    async def deactivate_session(self, session_id: UUID) -> None:
        now = datetime.utcnow()
        query = """
            UPDATE user_sessions
            SET is_active = FALSE, logout_at = $1, updated_at = $2
            WHERE id = $3 AND is_deleted = FALSE
        """
        await self.db_object.execute(query, now, now, session_id)
