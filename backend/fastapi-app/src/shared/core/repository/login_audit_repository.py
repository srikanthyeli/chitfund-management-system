from uuid import UUID
import uuid
from typing import Optional
from datetime import datetime, timezone
from src.api.models.models import LoginAuditLog

class LoginAuditRepository:
    def __init__(self, db_object):
        self.db_object = db_object

    async def create_log(self, event_type: str, user_id: Optional[UUID] = None, mobile: Optional[str] = None, ip_address: Optional[str] = None, device_id: Optional[str] = None, remarks: Optional[str] = None) -> LoginAuditLog:
        log_id = uuid.uuid4()
        now = datetime.utcnow()
        query = """
            INSERT INTO login_audit_logs (id, user_id, mobile, event_type, ip_address, device_id, remarks, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id, user_id, mobile, event_type, ip_address, device_id, remarks, created_at
        """
        row = await self.db_object.fetchrow(
            query,
            log_id, user_id, mobile, event_type, ip_address, device_id, remarks, now
        )
        return LoginAuditLog(**dict(row))
