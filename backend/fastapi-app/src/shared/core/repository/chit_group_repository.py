from uuid import UUID
import uuid
from typing import Optional, List, Tuple
from datetime import datetime, date
from decimal import Decimal
from src.api.models.models import ChitGroup

class ChitGroupRepository:
    def __init__(self, db_object):
        self.db_object = db_object

    async def get_next_chit_sequence_for_organizer(self, organizer_id: UUID) -> str:
        # Lock the organizer row to prevent race conditions during chit code generation
        await self.db_object.execute("SELECT 1 FROM organizers WHERE id = $1 FOR UPDATE", organizer_id)
        
        # Get count of chit groups
        query = "SELECT COUNT(id) FROM chit_groups WHERE organizer_id = $1"
        count = await self.db_object.fetchval(query, organizer_id)
        return f"CHIT{(count + 1):05d}"

    async def get_chit_group_by_id_and_organizer(self, chit_group_id: UUID, organizer_id: UUID) -> Optional[ChitGroup]:
        query = """
            SELECT * FROM chit_groups 
            WHERE id = $1 AND organizer_id = $2 AND is_deleted = FALSE
        """
        row = await self.db_object.fetchrow(query, chit_group_id, organizer_id)
        if row:
            return ChitGroup(**dict(row))
        return None

    async def get_chit_group_by_name_and_organizer(self, chit_name: str, organizer_id: UUID) -> Optional[ChitGroup]:
        query = """
            SELECT * FROM chit_groups 
            WHERE chit_name = $1 AND organizer_id = $2 AND is_deleted = FALSE
        """
        row = await self.db_object.fetchrow(query, chit_name, organizer_id)
        if row:
            return ChitGroup(**dict(row))
        return None

    async def get_chit_group_by_code_and_organizer(self, chit_code: str, organizer_id: UUID) -> Optional[ChitGroup]:
        query = """
            SELECT * FROM chit_groups 
            WHERE chit_code = $1 AND organizer_id = $2 AND is_deleted = FALSE
        """
        row = await self.db_object.fetchrow(query, chit_code, organizer_id)
        if row:
            return ChitGroup(**dict(row))
        return None

    async def create_chit_group(self, data: dict, created_by: UUID) -> ChitGroup:
        chit_id = uuid.uuid4()
        now = datetime.utcnow()
        code = await self.get_next_chit_sequence_for_organizer(data["organizer_id"])
        
        query = """
            INSERT INTO chit_groups (
                id, organizer_id, chit_code, chit_name, description, 
                total_chit_value, monthly_installment_per_share, total_shares, 
                duration_months, maintenance_charge, maintenance_charge_type, 
                start_date, installment_due_day, status, allocated_shares, available_shares,
                created_at, created_by, is_deleted, version
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, FALSE, 1)
            RETURNING *
        """
        row = await self.db_object.fetchrow(
            query,
            chit_id,
            data["organizer_id"],
            code,
            data["chit_name"],
            data.get("description"),
            Decimal(str(data["total_chit_value"])),
            Decimal(str(data["monthly_installment_per_share"])),
            data["total_shares"],
            data["duration_months"],
            Decimal(str(data.get("maintenance_charge", 0))),
            data.get("maintenance_charge_type", "FIXED"),
            data["start_date"],
            data.get("installment_due_day", 1),
            "DRAFT",
            0,
            data["total_shares"],
            now,
            created_by
        )
        return ChitGroup(**dict(row))

    async def list_chit_groups(
        self, 
        organizer_id: UUID, 
        skip: int = 0, 
        limit: int = 20, 
        search: Optional[str] = None, 
        status: Optional[str] = None, 
        start_date_from: Optional[date] = None,
        start_date_to: Optional[date] = None,
        sort_by: str = 'start_date', 
        sort_order: str = 'desc'
    ) -> Tuple[List[ChitGroup], int]:
        allowed_sort_fields = {'created_at', 'start_date', 'chit_name', 'chit_code', 'total_chit_value', 'status'}
        if sort_by not in allowed_sort_fields:
            sort_by = 'start_date'
        
        sort_order = sort_order.lower()
        if sort_order not in {'asc', 'desc'}:
            sort_order = 'desc'

        base_where = "WHERE organizer_id = $1 AND is_deleted = FALSE"
        params = [organizer_id]
        param_count = 1

        if status:
            param_count += 1
            base_where += f" AND status = ${param_count}"
            params.append(status)

        if search:
            param_count += 1
            search_pattern = f"%{search}%"
            base_where += f" AND (chit_name ILIKE ${param_count} OR chit_code ILIKE ${param_count})"
            params.append(search_pattern)

        if start_date_from:
            param_count += 1
            base_where += f" AND start_date >= ${param_count}"
            params.append(start_date_from)

        if start_date_to:
            param_count += 1
            base_where += f" AND start_date <= ${param_count}"
            params.append(start_date_to)

        # Count query
        count_query = f"SELECT COUNT(id) FROM chit_groups {base_where}"
        total = await self.db_object.fetchval(count_query, *params)

        # Pagination
        param_count += 1
        limit_param = param_count
        param_count += 1
        offset_param = param_count
        params.extend([limit, skip])

        select_query = f"""
            SELECT * FROM chit_groups
            {base_where}
            ORDER BY {sort_by} {sort_order}
            LIMIT ${limit_param} OFFSET ${offset_param}
        """
        rows = await self.db_object.fetch(select_query, *params)
        chits = [ChitGroup(**dict(row)) for row in rows]
        return chits, total

    async def update_chit_group(self, chit_group_id: UUID, organizer_id: UUID, data: dict, updated_by: UUID) -> Optional[ChitGroup]:
        set_clauses = []
        values = []
        i = 1
        for k, v in data.items():
            set_clauses.append(f"{k} = ${i}")
            if isinstance(v, (int, float, Decimal)) and k in ('total_chit_value', 'monthly_installment_per_share', 'maintenance_charge'):
                values.append(Decimal(str(v)))
            else:
                values.append(v)
            i += 1

        if not set_clauses:
            return await self.get_chit_group_by_id_and_organizer(chit_group_id, organizer_id)

        set_clauses.append(f"updated_at = ${i}")
        values.append(datetime.utcnow())
        i += 1

        set_clauses.append(f"updated_by = ${i}")
        values.append(updated_by)
        i += 1

        set_clauses.append(f"version = version + 1")

        values.append(chit_group_id)
        chit_group_id_param = i
        i += 1

        values.append(organizer_id)
        organizer_id_param = i

        query = f"""
            UPDATE chit_groups
            SET {', '.join(set_clauses)}
            WHERE id = ${chit_group_id_param} AND organizer_id = ${organizer_id_param} AND is_deleted = FALSE
            RETURNING *
        """
        row = await self.db_object.fetchrow(query, *values)
        if row:
            return ChitGroup(**dict(row))
        return None

    async def update_chit_group_status(self, chit_group_id: UUID, organizer_id: UUID, status: str, updated_by: UUID) -> Optional[ChitGroup]:
        query = """
            UPDATE chit_groups
            SET status = $1, updated_at = $2, updated_by = $3, version = version + 1
            WHERE id = $4 AND organizer_id = $5 AND is_deleted = FALSE
            RETURNING *
        """
        row = await self.db_object.fetchrow(query, status, datetime.utcnow(), updated_by, chit_group_id, organizer_id)
        if row:
            return ChitGroup(**dict(row))
        return None

    async def update_share_counts(self, chit_group_id: UUID, organizer_id: UUID, allocated: int, available: int, updated_by: UUID) -> Optional[ChitGroup]:
        query = """
            UPDATE chit_groups
            SET allocated_shares = $1, available_shares = $2, updated_at = $3, updated_by = $4, version = version + 1
            WHERE id = $5 AND organizer_id = $6 AND is_deleted = FALSE
            RETURNING *
        """
        row = await self.db_object.fetchrow(query, allocated, available, datetime.utcnow(), updated_by, chit_group_id, organizer_id)
        if row:
            return ChitGroup(**dict(row))
        return None

    async def get_chit_group_summary(self, organizer_id: UUID) -> dict:
        total_query = "SELECT COUNT(id) FROM chit_groups WHERE organizer_id = $1 AND is_deleted = FALSE"
        draft_query = "SELECT COUNT(id) FROM chit_groups WHERE organizer_id = $1 AND status = 'DRAFT' AND is_deleted = FALSE"
        ready_query = "SELECT COUNT(id) FROM chit_groups WHERE organizer_id = $1 AND status = 'READY_TO_START' AND is_deleted = FALSE"
        active_query = "SELECT COUNT(id) FROM chit_groups WHERE organizer_id = $1 AND status = 'ACTIVE' AND is_deleted = FALSE"
        
        allocated_shares_query = "SELECT COALESCE(SUM(allocated_shares), 0) FROM chit_groups WHERE organizer_id = $1 AND is_deleted = FALSE"
        available_shares_query = "SELECT COALESCE(SUM(available_shares), 0) FROM chit_groups WHERE organizer_id = $1 AND is_deleted = FALSE"
        
        now = datetime.utcnow().date()
        upcoming_query = "SELECT COUNT(id) FROM chit_groups WHERE organizer_id = $1 AND start_date > $2 AND is_deleted = FALSE"

        total = await self.db_object.fetchval(total_query, organizer_id) or 0
        draft = await self.db_object.fetchval(draft_query, organizer_id) or 0
        ready = await self.db_object.fetchval(ready_query, organizer_id) or 0
        active = await self.db_object.fetchval(active_query, organizer_id) or 0
        allocated = await self.db_object.fetchval(allocated_shares_query, organizer_id) or 0
        available = await self.db_object.fetchval(available_shares_query, organizer_id) or 0
        upcoming = await self.db_object.fetchval(upcoming_query, organizer_id, now) or 0

        return {
            "total_chits": total,
            "draft_chits": draft,
            "ready_to_start_chits": ready,
            "active_chits": active,
            "total_allocated_shares": allocated,
            "total_available_shares": available,
            "upcoming_chits_count": upcoming
        }
