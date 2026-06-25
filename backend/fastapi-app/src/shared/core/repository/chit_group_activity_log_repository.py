from uuid import UUID
import uuid
import json
from typing import Optional, List, Tuple
from datetime import datetime
from src.api.models.models import ChitGroupActivityLog

class ChitGroupActivityLogRepository:
    def __init__(self, db_object):
        self.db_object = db_object

    async def create_log(
        self,
        organizer_id: UUID,
        chit_group_id: UUID,
        action_type: str,
        membership_id: Optional[UUID] = None,
        old_values: Optional[dict] = None,
        new_values: Optional[dict] = None,
        remarks: Optional[str] = None,
        performed_by_user_id: Optional[UUID] = None
    ) -> ChitGroupActivityLog:
        log_id = uuid.uuid4()
        now = datetime.utcnow()
        
        old_values_json = json.dumps(old_values) if old_values is not None else None
        new_values_json = json.dumps(new_values) if new_values is not None else None

        query = """
            INSERT INTO chit_group_activity_logs (
                id, organizer_id, chit_group_id, membership_id, action_type, 
                old_values, new_values, remarks, performed_by_user_id, created_at
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            RETURNING id, organizer_id, chit_group_id, membership_id, action_type, old_values, new_values, remarks, performed_by_user_id, created_at
        """
        row = await self.db_object.fetchrow(
            query,
            log_id,
            organizer_id,
            chit_group_id,
            membership_id,
            action_type,
            old_values_json,
            new_values_json,
            remarks,
            performed_by_user_id,
            now
        )
        
        row_dict = dict(row)
        if row_dict.get("old_values") and isinstance(row_dict["old_values"], str):
            row_dict["old_values"] = json.loads(row_dict["old_values"])
        if row_dict.get("new_values") and isinstance(row_dict["new_values"], str):
            row_dict["new_values"] = json.loads(row_dict["new_values"])

        return ChitGroupActivityLog(**row_dict)

    async def get_chit_group_activity_logs(
        self,
        chit_group_id: UUID,
        organizer_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[ChitGroupActivityLog], int]:
        count_query = """
            SELECT COUNT(id) 
            FROM chit_group_activity_logs 
            WHERE chit_group_id = $1 AND organizer_id = $2
        """
        total = await self.db_object.fetchval(count_query, chit_group_id, organizer_id) or 0

        query = """
            SELECT id, organizer_id, chit_group_id, membership_id, action_type, old_values, new_values, remarks, performed_by_user_id, created_at
            FROM chit_group_activity_logs
            WHERE chit_group_id = $1 AND organizer_id = $2
            ORDER BY created_at DESC
            LIMIT $3 OFFSET $4
        """
        rows = await self.db_object.fetch(query, chit_group_id, organizer_id, limit, skip)
        
        logs = []
        for row in rows:
            row_dict = dict(row)
            if row_dict.get("old_values") and isinstance(row_dict["old_values"], str):
                row_dict["old_values"] = json.loads(row_dict["old_values"])
            if row_dict.get("new_values") and isinstance(row_dict["new_values"], str):
                row_dict["new_values"] = json.loads(row_dict["new_values"])
            logs.append(ChitGroupActivityLog(**row_dict))

        return logs, total
