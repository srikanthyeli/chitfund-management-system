from uuid import UUID
import uuid
from typing import Optional, List, Tuple
from datetime import datetime, timezone
from src.api.models.models import Organizer

class OrganizerRepository:
    def __init__(self, db_object):
        self.db_object = db_object

    async def get_organizer_by_id(self, organizer_id: UUID) -> Optional[Organizer]:
        query = """
            SELECT id, organizer_code, name, mobile, email, address, village, mandal, district, state, pincode, is_active, created_at
            FROM organizers 
            WHERE id = $1 AND is_deleted = FALSE
        """
        row = await self.db_object.fetchrow(query, organizer_id)
        if row:
            return Organizer(**dict(row))
        return None

    async def get_organizer_by_mobile(self, mobile: str) -> Optional[Organizer]:
        query = """
            SELECT id, organizer_code, name, mobile, email, address, village, mandal, district, state, pincode, is_active, created_at
            FROM organizers 
            WHERE mobile = $1 AND is_deleted = FALSE
        """
        row = await self.db_object.fetchrow(query, mobile)
        if row:
            return Organizer(**dict(row))
        return None

    async def get_organizer_by_email(self, email: str) -> Optional[Organizer]:
        query = """
            SELECT id, organizer_code, name, mobile, email, address, village, mandal, district, state, pincode, is_active, created_at
            FROM organizers 
            WHERE email = $1 AND is_deleted = FALSE
        """
        row = await self.db_object.fetchrow(query, email)
        if row:
            return Organizer(**dict(row))
        return None

    async def get_next_organizer_code(self) -> str:
        query = "SELECT COUNT(id) FROM organizers WHERE is_deleted = FALSE"
        count = await self.db_object.fetchval(query)
        return f"ORG{(count + 1):05d}"

    async def create_organizer(self, data: dict, created_by: UUID) -> Organizer:
        organizer_id = uuid.uuid4()
        now = datetime.utcnow()
        code = await self.get_next_organizer_code()
        
        query = """
            INSERT INTO organizers (id, organizer_code, name, mobile, email, address, village, mandal, district, state, pincode, is_active, created_at, created_by, is_deleted, version)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, FALSE, 1)
            RETURNING id, organizer_code, name, mobile, email, address, village, mandal, district, state, pincode, is_active, created_at
        """
        row = await self.db_object.fetchrow(
            query,
            organizer_id,
            code,
            data["name"],
            data["mobile"],
            data.get("email"),
            data.get("address"),
            data.get("village"),
            data.get("mandal"),
            data.get("district"),
            data.get("state"),
            data.get("pincode"),
            True,
            now,
            created_by
        )
        return Organizer(**dict(row))

    async def get_all_organizers(self, skip: int = 0, limit: int = 100) -> Tuple[List[Organizer], int]:
        count_query = "SELECT COUNT(id) FROM organizers WHERE is_deleted = FALSE"
        total = await self.db_object.fetchval(count_query)
        
        query = """
            SELECT id, organizer_code, name, mobile, email, address, village, mandal, district, state, pincode, is_active, created_at
            FROM organizers 
            WHERE is_deleted = FALSE
            ORDER BY created_at DESC
            LIMIT $1 OFFSET $2
        """
        rows = await self.db_object.fetch(query, limit, skip)
        organizers = [Organizer(**dict(row)) for row in rows]
        return organizers, total

    async def update_organizer_status(self, organizer_id: UUID, is_active: bool, updated_by: UUID) -> None:
        query = """
            UPDATE organizers 
            SET is_active = $1, updated_at = $2, updated_by = $3
            WHERE id = $4 AND is_deleted = FALSE
        """
        await self.db_object.execute(query, is_active, datetime.utcnow(), updated_by, organizer_id)

    async def update_organizer(self, organizer_id: UUID, data: dict, updated_by: UUID) -> Optional[Organizer]:
        # Simple dynamic update
        set_clauses = []
        values = []
        i = 1
        for k, v in data.items():
            if v is not None:
                set_clauses.append(f"{k} = ${i}")
                values.append(v)
                i += 1
                
        if not set_clauses:
            return await self.get_organizer_by_id(organizer_id)
            
        set_clauses.append(f"updated_at = ${i}")
        values.append(datetime.utcnow())
        i += 1
        
        set_clauses.append(f"updated_by = ${i}")
        values.append(updated_by)
        i += 1
        
        values.append(organizer_id)
        
        query = f"""
            UPDATE organizers
            SET {', '.join(set_clauses)}
            WHERE id = ${i} AND is_deleted = FALSE
            RETURNING id, organizer_code, name, mobile, email, address, village, mandal, district, state, pincode, is_active, created_at
        """
        row = await self.db_object.fetchrow(query, *values)
        if row:
            return Organizer(**dict(row))
        return None
