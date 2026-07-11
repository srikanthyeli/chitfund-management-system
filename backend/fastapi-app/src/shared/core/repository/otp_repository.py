from uuid import UUID
import uuid
from typing import Optional
from datetime import datetime
from src.api.models.models import OTPRequest

class OTPRepository:
    def __init__(self, db_object):
        self.db = db_object

    async def create_otp_request(self, mobile: str, otp_hash: str, expires_at: datetime) -> OTPRequest:
        query = """
            INSERT INTO otp_requests (id, mobile, otp_hash, expires_at, attempts, is_used, created_at)
            VALUES ($1, $2, $3, $4, 0, FALSE, $5)
            RETURNING id, mobile, otp_hash, expires_at, attempts, is_used, created_at
        """
        row = await self.db.fetchrow(
            query, uuid.uuid4(), mobile, otp_hash, expires_at, datetime.utcnow()
        )
        if row:
            return OTPRequest(**dict(row))
        return None

    async def get_latest_otp_request(self, mobile: str) -> Optional[OTPRequest]:
        query = """
            SELECT id, mobile, otp_hash, expires_at, attempts, is_used, created_at
            FROM otp_requests
            WHERE mobile = $1
            ORDER BY created_at DESC
            LIMIT 1
        """
        row = await self.db.fetchrow(query, mobile)
        if row:
            return OTPRequest(**dict(row))
        return None

    async def increment_attempts(self, otp_id: UUID) -> None:
        query = """
            UPDATE otp_requests
            SET attempts = attempts + 1
            WHERE id = $1
        """
        await self.db.execute(query, otp_id)

    async def mark_as_used(self, otp_id: UUID) -> None:
        query = """
            UPDATE otp_requests
            SET is_used = TRUE
            WHERE id = $1
        """
        await self.db.execute(query, otp_id)

    async def count_recent_requests(self, mobile: str, since: datetime) -> int:
        query = """
            SELECT count(*)
            FROM otp_requests
            WHERE mobile = $1 AND created_at >= $2
        """
        val = await self.db.fetchval(query, mobile, since)
        return val or 0
