from uuid import UUID
import uuid
from typing import Optional, List, Tuple
from datetime import datetime
from src.api.models.models import Member

class MemberRepository:
    def __init__(self, db_object):
        self.db_object = db_object

    async def get_next_member_sequence_for_organizer(self, organizer_id: UUID) -> str:
        # Lock the organizer row to prevent race conditions during member code generation
        await self.db_object.execute("SELECT 1 FROM organizers WHERE id = $1 FOR UPDATE", organizer_id)
        
        # Get count of members
        query = "SELECT COUNT(id) FROM members WHERE organizer_id = $1"
        count = await self.db_object.fetchval(query, organizer_id)
        return f"MEM{(count + 1):05d}"

    async def get_member_by_id_and_organizer(self, member_id: UUID, organizer_id: UUID) -> Optional[Member]:
        query = """
            SELECT id, organizer_id, member_code, full_name, mobile, alternate_mobile, email, address, village, mandal, district, state, pincode, aadhaar_last4, notes, is_active, created_at, updated_at
            FROM members 
            WHERE id = $1 AND organizer_id = $2 AND is_deleted = FALSE
        """
        row = await self.db_object.fetchrow(query, member_id, organizer_id)
        if row:
            return Member(**dict(row))
        return None

    async def get_member_by_mobile_and_organizer(self, mobile: str, organizer_id: UUID) -> Optional[Member]:
        query = """
            SELECT id, organizer_id, member_code, full_name, mobile, alternate_mobile, email, address, village, mandal, district, state, pincode, aadhaar_last4, notes, is_active, created_at, updated_at
            FROM members 
            WHERE mobile = $1 AND organizer_id = $2 AND is_deleted = FALSE
        """
        row = await self.db_object.fetchrow(query, mobile, organizer_id)
        if row:
            return Member(**dict(row))
        return None

    async def get_member_by_code_and_organizer(self, member_code: str, organizer_id: UUID) -> Optional[Member]:
        query = """
            SELECT id, organizer_id, member_code, full_name, mobile, alternate_mobile, email, address, village, mandal, district, state, pincode, aadhaar_last4, notes, is_active, created_at, updated_at
            FROM members 
            WHERE member_code = $1 AND organizer_id = $2 AND is_deleted = FALSE
        """
        row = await self.db_object.fetchrow(query, member_code, organizer_id)
        if row:
            return Member(**dict(row))
        return None

    async def create_member(self, data: dict, created_by: UUID) -> Member:
        member_id = uuid.uuid4()
        now = datetime.utcnow()
        code = await self.get_next_member_sequence_for_organizer(data["organizer_id"])
        
        query = """
            INSERT INTO members (
                id, organizer_id, member_code, full_name, mobile, alternate_mobile, email, address, 
                village, mandal, district, state, pincode, aadhaar_last4, notes, is_active, 
                created_at, created_by, is_deleted, version
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, FALSE, 1)
            RETURNING id, organizer_id, member_code, full_name, mobile, alternate_mobile, email, address, village, mandal, district, state, pincode, aadhaar_last4, notes, is_active, created_at, updated_at
        """
        row = await self.db_object.fetchrow(
            query,
            member_id,
            data["organizer_id"],
            code,
            data["full_name"],
            data["mobile"],
            data.get("alternate_mobile"),
            data.get("email"),
            data.get("address"),
            data.get("village"),
            data.get("mandal"),
            data.get("district"),
            data.get("state"),
            data.get("pincode"),
            data.get("aadhaar_last4"),
            data.get("notes"),
            True,
            now,
            created_by
        )
        return Member(**dict(row))

    async def list_members(
        self, 
        organizer_id: UUID, 
        skip: int = 0, 
        limit: int = 20, 
        search: Optional[str] = None, 
        is_active: Optional[bool] = None, 
        sort_by: str = 'created_at', 
        sort_order: str = 'desc'
    ) -> Tuple[List[Member], int]:
        # Validate sort fields to prevent SQL injection
        allowed_sort_fields = {'created_at', 'full_name', 'mobile', 'member_code', 'village'}
        if sort_by not in allowed_sort_fields:
            sort_by = 'created_at'
        
        sort_order = sort_order.lower()
        if sort_order not in {'asc', 'desc'}:
            sort_order = 'desc'

        # Build dynamic queries
        base_where = "WHERE organizer_id = $1 AND is_deleted = FALSE"
        params = [organizer_id]
        param_count = 1

        if is_active is not None:
            param_count += 1
            base_where += f" AND is_active = ${param_count}"
            params.append(is_active)

        if search:
            param_count += 1
            search_pattern = f"%{search}%"
            base_where += f" AND (full_name ILIKE ${param_count} OR mobile ILIKE ${param_count} OR member_code ILIKE ${param_count})"
            params.append(search_pattern)

        # Count query
        count_query = f"SELECT COUNT(id) FROM members {base_where}"
        total = await self.db_object.fetchval(count_query, *params)

        # Pagination params
        param_count += 1
        limit_param = param_count
        param_count += 1
        offset_param = param_count
        params.extend([limit, skip])

        # Select query
        select_query = f"""
            SELECT id, organizer_id, member_code, full_name, mobile, alternate_mobile, email, address, village, mandal, district, state, pincode, aadhaar_last4, notes, is_active, created_at, updated_at
            FROM members
            {base_where}
            ORDER BY {sort_by} {sort_order}
            LIMIT ${limit_param} OFFSET ${offset_param}
        """
        rows = await self.db_object.fetch(select_query, *params)
        members = [Member(**dict(row)) for row in rows]
        return members, total

    async def update_member(self, member_id: UUID, organizer_id: UUID, data: dict, updated_by: UUID) -> Optional[Member]:
        set_clauses = []
        values = []
        i = 1
        for k, v in data.items():
            set_clauses.append(f"{k} = ${i}")
            values.append(v)
            i += 1

        if not set_clauses:
            return await self.get_member_by_id_and_organizer(member_id, organizer_id)

        set_clauses.append(f"updated_at = ${i}")
        values.append(datetime.utcnow())
        i += 1

        set_clauses.append(f"updated_by = ${i}")
        values.append(updated_by)
        i += 1

        # Add member_id and organizer_id to values
        values.append(member_id)
        member_id_param = i
        i += 1

        values.append(organizer_id)
        organizer_id_param = i

        query = f"""
            UPDATE members
            SET {', '.join(set_clauses)}
            WHERE id = ${member_id_param} AND organizer_id = ${organizer_id_param} AND is_deleted = FALSE
            RETURNING id, organizer_id, member_code, full_name, mobile, alternate_mobile, email, address, village, mandal, district, state, pincode, aadhaar_last4, notes, is_active, created_at, updated_at
        """
        row = await self.db_object.fetchrow(query, *values)
        if row:
            return Member(**dict(row))
        return None

    async def update_member_mobile(self, member_id: UUID, organizer_id: UUID, new_mobile: str, updated_by: UUID) -> Optional[Member]:
        query = """
            UPDATE members
            SET mobile = $1, updated_at = $2, updated_by = $3
            WHERE id = $4 AND organizer_id = $5 AND is_deleted = FALSE
            RETURNING id, organizer_id, member_code, full_name, mobile, alternate_mobile, email, address, village, mandal, district, state, pincode, aadhaar_last4, notes, is_active, created_at, updated_at
        """
        row = await self.db_object.fetchrow(query, new_mobile, datetime.utcnow(), updated_by, member_id, organizer_id)
        if row:
            return Member(**dict(row))
        return None

    async def update_member_status(self, member_id: UUID, organizer_id: UUID, is_active: bool, updated_by: UUID) -> Optional[Member]:
        query = """
            UPDATE members
            SET is_active = $1, updated_at = $2, updated_by = $3
            WHERE id = $4 AND organizer_id = $5 AND is_deleted = FALSE
            RETURNING id, organizer_id, member_code, full_name, mobile, alternate_mobile, email, address, village, mandal, district, state, pincode, aadhaar_last4, notes, is_active, created_at, updated_at
        """
        row = await self.db_object.fetchrow(query, is_active, datetime.utcnow(), updated_by, member_id, organizer_id)
        if row:
            return Member(**dict(row))
        return None

    async def get_member_summary(self, organizer_id: UUID) -> dict:
        total_query = "SELECT COUNT(id) FROM members WHERE organizer_id = $1 AND is_deleted = FALSE"
        active_query = "SELECT COUNT(id) FROM members WHERE organizer_id = $1 AND is_active = TRUE AND is_deleted = FALSE"
        inactive_query = "SELECT COUNT(id) FROM members WHERE organizer_id = $1 AND is_active = FALSE AND is_deleted = FALSE"
        
        now = datetime.utcnow()
        start_of_month = datetime(now.year, now.month, 1)
        new_query = "SELECT COUNT(id) FROM members WHERE organizer_id = $1 AND is_deleted = FALSE AND created_at >= $2"

        total = await self.db_object.fetchval(total_query, organizer_id) or 0
        active = await self.db_object.fetchval(active_query, organizer_id) or 0
        inactive = await self.db_object.fetchval(inactive_query, organizer_id) or 0
        new_this_month = await self.db_object.fetchval(new_query, organizer_id, start_of_month) or 0

        return {
            "total_members": total,
            "active_members": active,
            "inactive_members": inactive,
            "new_members_this_month": new_this_month
        }

    async def get_members_by_ids_and_organizer(self, member_ids: List[UUID], organizer_id: UUID) -> List[Member]:
        if not member_ids:
            return []
        query = """
            SELECT id, organizer_id, member_code, full_name, mobile, alternate_mobile, email, address, village, mandal, district, state, pincode, aadhaar_last4, notes, is_active, created_at, updated_at
            FROM members 
            WHERE id = ANY($1) AND organizer_id = $2 AND is_deleted = FALSE
        """
        rows = await self.db_object.fetch(query, member_ids, organizer_id)
        return [Member(**dict(row)) for row in rows]

