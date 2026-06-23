from uuid import UUID
import uuid
from typing import Optional
from datetime import datetime
from src.api.models.models import User

class UserRepository:
    def __init__(self, db_object):
        self.db_object = db_object

    async def get_user_by_mobile(self, mobile: str) -> Optional[User]:
        """
        Retrieves a user by their mobile number using raw SQL with $1 parameters.
        """
        query = """
            SELECT id, mobile, password_hash, otp_enabled, role, is_active, last_login_at 
            FROM users 
            WHERE mobile = $1 AND is_deleted = FALSE
        """
        row = await self.db_object.fetchrow(query, mobile)
        if row:
            return User(
                id=row["id"],
                mobile=row["mobile"],
                password_hash=row["password_hash"],
                otp_enabled=row["otp_enabled"],
                role=row["role"],
                is_active=row["is_active"],
                last_login_at=row["last_login_at"]
            )
        return None

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """
        Retrieves a user by their unique UUID using raw SQL with $1 parameters.
        """
        query = """
            SELECT id, mobile, password_hash, otp_enabled, role, is_active, last_login_at 
            FROM users 
            WHERE id = $1 AND is_deleted = FALSE
        """
        row = await self.db_object.fetchrow(query, user_id)
        if row:
            return User(
                id=row["id"],
                mobile=row["mobile"],
                password_hash=row["password_hash"],
                otp_enabled=row["otp_enabled"],
                role=row["role"],
                is_active=row["is_active"],
                last_login_at=row["last_login_at"]
            )
        return None

    async def create_user(self, user_data: dict) -> Optional[User]:
        """
        Creates a new user record using raw SQL with $1, $2 parameters.
        """
        user_id = user_data.get("id") or uuid.uuid4()
        query = """
            INSERT INTO users (id, mobile, password_hash, otp_enabled, role, is_active, created_at, is_deleted, version)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING id, mobile, password_hash, otp_enabled, role, is_active, last_login_at
        """
        row = await self.db_object.fetchrow(
            query,
            user_id,
            user_data["mobile"],
            user_data["password_hash"],
            user_data.get("otp_enabled", True),
            user_data.get("role", "MEMBER"),
            user_data.get("is_active", True),
            datetime.utcnow(),
            False,
            1
        )
        if row:
            return User(
                id=row["id"],
                mobile=row["mobile"],
                password_hash=row["password_hash"],
                otp_enabled=row["otp_enabled"],
                role=row["role"],
                is_active=row["is_active"],
                last_login_at=row["last_login_at"]
            )
        return None

    async def update_last_login(self, user_id: UUID) -> None:
        """
        Updates the last_login_at timestamp for the user using raw SQL with $1, $2 parameters.
        """
        query = """
            UPDATE users 
            SET last_login_at = $1 
            WHERE id = $2 AND is_deleted = FALSE
        """
        await self.db_object.execute(query, datetime.utcnow(), user_id)
