from uuid import UUID
import uuid
from typing import Optional, List
from datetime import datetime
from src.api.models.models import ChitMembership, ChitGroup

class ChitMembershipRepository:
    def __init__(self, db_object):
        self.db_object = db_object

    async def lock_chit_group_for_share_update(self, chit_group_id: UUID) -> Optional[dict]:
        query = """
            SELECT id, total_shares, allocated_shares, available_shares, status 
            FROM chit_groups 
            WHERE id = $1 AND is_deleted = FALSE 
            FOR UPDATE
        """
        row = await self.db_object.fetchrow(query, chit_group_id)
        return dict(row) if row else None

    async def get_total_allocated_shares(self, chit_group_id: UUID) -> int:
        query = """
            SELECT COALESCE(SUM(share_count), 0) 
            FROM chit_memberships 
            WHERE chit_group_id = $1 AND status = 'ACTIVE' AND is_deleted = FALSE
        """
        val = await self.db_object.fetchval(query, chit_group_id)
        return val or 0

    async def get_membership_by_id_and_organizer(self, membership_id: UUID, organizer_id: UUID) -> Optional[ChitMembership]:
        query = """
            SELECT * FROM chit_memberships 
            WHERE id = $1 AND organizer_id = $2 AND is_deleted = FALSE
        """
        row = await self.db_object.fetchrow(query, membership_id, organizer_id)
        if row:
            return ChitMembership(**dict(row))
        return None

    async def get_membership_by_chit_and_member(self, chit_group_id: UUID, member_id: UUID, organizer_id: UUID) -> Optional[ChitMembership]:
        query = """
            SELECT * FROM chit_memberships 
            WHERE chit_group_id = $1 AND member_id = $2 AND organizer_id = $3 AND is_deleted = FALSE
        """
        row = await self.db_object.fetchrow(query, chit_group_id, member_id, organizer_id)
        if row:
            return ChitMembership(**dict(row))
        return None

    async def create_membership(self, data: dict, created_by: UUID) -> ChitMembership:
        membership_id = uuid.uuid4()
        now = datetime.utcnow()
        
        query = """
            INSERT INTO chit_memberships (
                id, organizer_id, chit_group_id, member_id, 
                share_count, joined_at, status, remarks,
                created_at, created_by, is_deleted, version
            )
            VALUES ($1, $2, $3, $4, $5, $6, 'ACTIVE', $7, $8, $9, FALSE, 1)
            RETURNING *
        """
        row = await self.db_object.fetchrow(
            query,
            membership_id,
            data["organizer_id"],
            data["chit_group_id"],
            data["member_id"],
            data["share_count"],
            now,
            data.get("remarks"),
            now,
            created_by
        )
        return ChitMembership(**dict(row))

    async def update_membership_share_count(self, membership_id: UUID, organizer_id: UUID, share_count: int, remarks: Optional[str], updated_by: UUID) -> Optional[ChitMembership]:
        query = """
            UPDATE chit_memberships
            SET share_count = $1, remarks = COALESCE($2, remarks), updated_at = $3, updated_by = $4, version = version + 1
            WHERE id = $5 AND organizer_id = $6 AND is_deleted = FALSE
            RETURNING *
        """
        row = await self.db_object.fetchrow(query, share_count, remarks, datetime.utcnow(), updated_by, membership_id, organizer_id)
        if row:
            return ChitMembership(**dict(row))
        return None

    async def soft_remove_membership(self, membership_id: UUID, organizer_id: UUID, remarks: Optional[str], deleted_by: UUID) -> Optional[ChitMembership]:
        query = """
            UPDATE chit_memberships
            SET status = 'REMOVED', remarks = COALESCE($1, remarks), is_deleted = TRUE, deleted_at = $2, deleted_by = $3, version = version + 1
            WHERE id = $4 AND organizer_id = $5 AND is_deleted = FALSE
            RETURNING *
        """
        row = await self.db_object.fetchrow(query, remarks, datetime.utcnow(), deleted_by, membership_id, organizer_id)
        if row:
            return ChitMembership(**dict(row))
        return None

    async def list_memberships_by_chit_group(self, chit_group_id: UUID, organizer_id: UUID) -> List[dict]:
        query = """
            SELECT 
                cm.id as membership_id,
                cm.member_id,
                m.member_code,
                m.full_name,
                m.mobile,
                m.village,
                cm.share_count,
                cm.status as membership_status
            FROM chit_memberships cm
            JOIN members m ON cm.member_id = m.id
            WHERE cm.chit_group_id = $1 AND cm.organizer_id = $2 AND cm.is_deleted = FALSE AND m.is_deleted = FALSE
            ORDER BY cm.created_at ASC
        """
        rows = await self.db_object.fetch(query, chit_group_id, organizer_id)
        return [dict(row) for row in rows]

    async def get_chit_group_for_update(self, chit_group_id: UUID) -> Optional[ChitGroup]:
        query = """
            SELECT * FROM chit_groups 
            WHERE id = $1 AND is_deleted = FALSE 
            FOR UPDATE
        """
        row = await self.db_object.fetchrow(query, chit_group_id)
        return ChitGroup(**dict(row)) if row else None

    async def get_existing_memberships_for_update(self, chit_group_id: UUID, member_ids: List[UUID]) -> List[ChitMembership]:
        if not member_ids:
            return []
        query = """
            SELECT * FROM chit_memberships
            WHERE chit_group_id = $1 AND member_id = ANY($2) AND status = 'ACTIVE' AND is_deleted = FALSE
            FOR UPDATE
        """
        rows = await self.db_object.fetch(query, chit_group_id, member_ids)
        return [ChitMembership(**dict(row)) for row in rows]

    async def bulk_create_memberships(self, memberships_data: List[dict], created_by: UUID) -> List[ChitMembership]:
        if not memberships_data:
            return []
        
        columns = [
            "id", "organizer_id", "chit_group_id", "member_id", 
            "share_count", "joined_at", "status", "remarks",
            "created_at", "created_by", "is_deleted", "version"
        ]
        
        now = datetime.utcnow()
        values = []
        placeholders = []
        idx = 1
        
        for data in memberships_data:
            row_placeholders = []
            m_id = uuid.uuid4()
            row_values = [
                m_id,
                data["organizer_id"],
                data["chit_group_id"],
                data["member_id"],
                data["share_count"],
                now,
                "ACTIVE",
                data.get("remarks"),
                now,
                created_by,
                False,
                1
            ]
            values.extend(row_values)
            for _ in row_values:
                row_placeholders.append(f"${idx}")
                idx += 1
            placeholders.append(f"({', '.join(row_placeholders)})")
            
        query = f"""
            INSERT INTO chit_memberships ({', '.join(columns)})
            VALUES {', '.join(placeholders)}
            RETURNING *
        """
        rows = await self.db_object.fetch(query, *values)
        return [ChitMembership(**dict(row)) for row in rows]

    async def bulk_increment_membership_shares(
        self, 
        membership_ids: List[UUID], 
        organizer_id: UUID,
        increment_count: int, 
        remarks: Optional[str], 
        updated_by: UUID
    ) -> List[ChitMembership]:
        if not membership_ids:
            return []
        
        query = """
            UPDATE chit_memberships
            SET 
                share_count = share_count + $1,
                remarks = COALESCE($2, remarks),
                updated_at = $3,
                updated_by = $4,
                version = version + 1
            WHERE id = ANY($5) AND organizer_id = $6 AND is_deleted = FALSE
            RETURNING *
        """
        rows = await self.db_object.fetch(query, increment_count, remarks, datetime.utcnow(), updated_by, membership_ids, organizer_id)
        return [ChitMembership(**dict(row)) for row in rows]

    async def list_active_memberships_with_members(self, chit_group_id: UUID, organizer_id: UUID) -> list:
        """Return active memberships with member info — used for dues generation and share totals."""
        query = """
            SELECT
                cm.id AS membership_id,
                cm.member_id,
                cm.share_count,
                cm.has_won_auction,
                cm.won_month_number,
                m.full_name,
                m.member_code,
                m.mobile,
                m.is_active AS member_is_active
            FROM chit_memberships cm
            JOIN members m ON m.id = cm.member_id
            WHERE cm.chit_group_id = $1
              AND cm.organizer_id = $2
              AND cm.status = 'ACTIVE'
              AND cm.is_deleted = FALSE
              AND m.is_deleted = FALSE
            ORDER BY cm.created_at ASC
        """
        rows = await self.db_object.fetch(query, chit_group_id, organizer_id)
        return [dict(row) for row in rows]

    async def mark_winner(
        self, membership_id: UUID, auction_id: UUID, month_number: int, updated_by: UUID
    ) -> None:
        """Mark a membership as having won an auction — prevents future bidding."""
        query = """
            UPDATE chit_memberships
            SET has_won_auction = TRUE,
                won_auction_id = $1,
                won_month_number = $2,
                updated_at = $3,
                updated_by = $4,
                version = version + 1
            WHERE id = $5 AND is_deleted = FALSE
        """
        await self.db_object.execute(
            query, auction_id, month_number, datetime.utcnow(), updated_by, membership_id
        )

