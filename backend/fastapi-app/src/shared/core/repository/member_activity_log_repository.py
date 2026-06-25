from uuid import UUID
import uuid
import json
from typing import Optional, List, Tuple
from datetime import datetime
from src.api.models.models import MemberActivityLog

class MemberActivityLogRepository:
    def __init__(self, db_object):
        self.db_object = db_object

    async def create_log(
        self,
        organizer_id: UUID,
        member_id: UUID,
        action_type: str,
        old_values: Optional[dict] = None,
        new_values: Optional[dict] = None,
        remarks: Optional[str] = None,
        performed_by: Optional[UUID] = None
    ) -> MemberActivityLog:
        log_id = uuid.uuid4()
        now = datetime.utcnow()
        
        # Serialize dict to JSON string for Postgres JSONB type compatibility
        old_values_json = json.dumps(old_values) if old_values is not None else None
        new_values_json = json.dumps(new_values) if new_values is not None else None

        query = """
            INSERT INTO member_activity_logs (
                id, organizer_id, member_id, action_type, old_values, new_values, remarks, performed_by, created_at
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING id, organizer_id, member_id, action_type, old_values, new_values, remarks, performed_by, created_at
        """
        row = await self.db_object.fetchrow(
            query,
            log_id,
            organizer_id,
            member_id,
            action_type,
            old_values_json,
            new_values_json,
            remarks,
            performed_by,
            now
        )
        
        # Parse JSON string back to dict if present for the returning model
        row_dict = dict(row)
        if row_dict.get("old_values"):
            row_dict["old_values"] = json.loads(row_dict["old_values"])
        if row_dict.get("new_values"):
            row_dict["new_values"] = json.loads(row_dict["new_values"])

        return MemberActivityLog(**row_dict)

    async def get_member_activity_logs(
        self,
        member_id: UUID,
        organizer_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[MemberActivityLog], int]:
        count_query = """
            SELECT COUNT(id) 
            FROM member_activity_logs 
            WHERE member_id = $1 AND organizer_id = $2
        """
        total = await self.db_object.fetchval(count_query, member_id, organizer_id) or 0

        query = """
            SELECT id, organizer_id, member_id, action_type, old_values, new_values, remarks, performed_by, created_at
            FROM member_activity_logs
            WHERE member_id = $1 AND organizer_id = $2
            ORDER BY created_at DESC
            LIMIT $3 OFFSET $4
        """
        rows = await self.db_object.fetch(query, member_id, organizer_id, limit, skip)
        
        logs = []
        for row in rows:
            row_dict = dict(row)
            if row_dict.get("old_values"):
                row_dict["old_values"] = json.loads(row_dict["old_values"])
            if row_dict.get("new_values"):
                row_dict["new_values"] = json.loads(row_dict["new_values"])
            logs.append(MemberActivityLog(**row_dict))

        return logs, total
