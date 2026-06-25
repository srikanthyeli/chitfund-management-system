from uuid import UUID
import uuid
from typing import Optional
from datetime import datetime, timezone
from src.api.models.models import User

class UserRepository:
    def __init__(self, db_object):
        self.db_object = db_object

    async def get_user_by_mobile(self, mobile: str) -> Optional[User]:
        query = """
            SELECT id, organizer_id, member_id, mobile, password_hash, role, is_active, last_login_at, must_change_password
            FROM users 
            WHERE mobile = $1 AND is_deleted = FALSE
        """
        row = await self.db_object.fetchrow(query, mobile)
        if row:
            return User(**dict(row))
        return None

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        query = """
            SELECT id, organizer_id, member_id, mobile, password_hash, role, is_active, last_login_at, must_change_password 
            FROM users 
            WHERE id = $1 AND is_deleted = FALSE
        """
        row = await self.db_object.fetchrow(query, user_id)
        if row:
            return User(**dict(row))
        return None

    async def create_user(self, user_data: dict) -> Optional[User]:
        user_id = user_data.get("id") or uuid.uuid4()
        now = datetime.utcnow()
        query = """
            INSERT INTO users (id, organizer_id, mobile, password_hash, role, is_active, must_change_password, created_at, is_deleted, version)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, FALSE, 1)
            RETURNING id, organizer_id, member_id, mobile, password_hash, role, is_active, last_login_at, must_change_password
        """
        row = await self.db_object.fetchrow(
            query,
            user_id,
            user_data.get("organizer_id"),
            user_data["mobile"],
            user_data["password_hash"],
            user_data.get("role", "MEMBER"),
            user_data.get("is_active", True),
            user_data.get("must_change_password", True),
            now
        )
        if row:
            return User(**dict(row))
        return None

    async def update_last_login(self, user_id: UUID) -> None:
        query = """
            UPDATE users 
            SET last_login_at = $1 
            WHERE id = $2 AND is_deleted = FALSE
        """
        await self.db_object.execute(query, datetime.utcnow(), user_id)

    async def update_user_status(self, user_id: UUID, is_active: bool) -> None:
        query = """
            UPDATE users 
            SET is_active = $1, updated_at = $2
            WHERE id = $3 AND is_deleted = FALSE
        """
        await self.db_object.execute(query, is_active, datetime.utcnow(), user_id)
