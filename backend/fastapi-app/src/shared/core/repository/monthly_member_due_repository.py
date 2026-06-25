from uuid import UUID
import uuid
from typing import List
from datetime import datetime
from decimal import Decimal


class MonthlyMemberDueRepository:
    def __init__(self, db_object):
        self.db = db_object

    async def bulk_create_dues(self, dues_data: List[dict], created_by: UUID) -> List[dict]:
        if not dues_data:
            return []

        now = datetime.utcnow()
        columns = [
            "id", "organizer_id", "chit_group_id", "chit_auction_id",
            "membership_id", "member_id", "month_number", "share_count",
            "gross_installment_amount", "bonus_per_share",
            "total_bonus_amount", "net_payable_amount",
            "total_paid_amount", "remaining_amount",
            "payment_status", "due_date", "remarks",
            "created_at", "created_by", "is_deleted", "version"
        ]

        values = []
        placeholders = []
        idx = 1

        for data in dues_data:
            due_id = uuid.uuid4()
            row_values = [
                due_id,
                data["organizer_id"],
                data["chit_group_id"],
                data["chit_auction_id"],
                data["membership_id"],
                data["member_id"],
                data["month_number"],
                data["share_count"],
                Decimal(str(data["gross_installment_amount"])),
                Decimal(str(data["bonus_per_share"])),
                Decimal(str(data["total_bonus_amount"])),
                Decimal(str(data["net_payable_amount"])),
                Decimal('0.00'),
                Decimal(str(data["net_payable_amount"])),
                "PENDING",
                data.get("due_date"),
                data.get("remarks"),
                now,
                created_by,
                False,
                1,
            ]
            row_ph = [f"${idx + i}" for i in range(len(row_values))]
            placeholders.append(f"({', '.join(row_ph)})")
            values.extend(row_values)
            idx += len(row_values)

        query = f"""
            INSERT INTO monthly_member_dues ({', '.join(columns)})
            VALUES {', '.join(placeholders)}
            RETURNING *
        """
        rows = await self.db.fetch(query, *values)
        return [dict(row) for row in rows]

    async def list_dues_by_auction(self, auction_id: UUID, organizer_id: UUID) -> List[dict]:
        query = """
            SELECT
                d.*,
                m.full_name AS member_name,
                m.mobile AS member_phone,
                m.member_code
            FROM monthly_member_dues d
            JOIN members m ON m.id = d.member_id
            WHERE d.chit_auction_id = $1 AND d.organizer_id = $2 AND d.is_deleted = FALSE
            ORDER BY m.full_name ASC
        """
        rows = await self.db.fetch(query, auction_id, organizer_id)
        return [dict(row) for row in rows]

    async def get_due_for_update(self, due_id: UUID, organizer_id: UUID) -> dict:
        query = """
            SELECT * FROM monthly_member_dues
            WHERE id = $1 AND organizer_id = $2 AND is_deleted = FALSE
            FOR UPDATE
        """
        row = await self.db.fetchrow(query, due_id, organizer_id)
        return dict(row) if row else None

    async def update_due_payment(self, due_id: UUID, organizer_id: UUID, 
                                 total_paid_amount: Decimal, remaining_amount: Decimal,
                                 payment_status: str, last_payment_at: datetime,
                                 updated_by: UUID) -> dict:
        now = datetime.utcnow()
        query = """
            UPDATE monthly_member_dues
            SET total_paid_amount = $3,
                remaining_amount = $4,
                payment_status = $5,
                last_payment_at = $6,
                updated_at = $7,
                updated_by = $8,
                version = version + 1
            WHERE id = $1 AND organizer_id = $2
            RETURNING *
        """
        row = await self.db.fetchrow(
            query, 
            due_id, organizer_id, 
            total_paid_amount, remaining_amount, 
            payment_status, last_payment_at, 
            now, updated_by
        )
        return dict(row) if row else None

    async def get_member_passbook_dues(self, member_id: UUID, organizer_id: UUID) -> List[dict]:
        query = """
            SELECT
                d.*,
                cg.chit_name,
                ca.auction_date,
                ca.auction_month_number
            FROM monthly_member_dues d
            JOIN chit_auctions ca ON d.chit_auction_id = ca.id
            JOIN chit_groups cg ON d.chit_group_id = cg.id
            WHERE d.member_id = $1 AND d.organizer_id = $2 AND d.is_deleted = FALSE
            ORDER BY cg.created_at ASC, ca.auction_month_number ASC
        """
        rows = await self.db.fetch(query, member_id, organizer_id)
        return [dict(row) for row in rows]

    async def get_active_collections_summary(self, organizer_id: UUID) -> List[dict]:
        query = """
            SELECT
                ca.id AS auction_id,
                ca.auction_month_number AS month_number,
                ca.status AS auction_status,
                cg.id AS chit_group_id,
                cg.chit_name,
                COUNT(d.id) AS total_memberships,
                COALESCE(SUM(d.net_payable_amount), 0) AS total_expected,
                COALESCE(SUM(d.total_paid_amount), 0) AS total_collected,
                COALESCE(SUM(d.remaining_amount), 0) AS total_remaining,
                COUNT(d.id) FILTER (WHERE d.payment_status = 'PAID') AS paid_count,
                COUNT(d.id) FILTER (WHERE d.payment_status = 'PARTIALLY_PAID') AS partial_count,
                COUNT(d.id) FILTER (WHERE d.payment_status = 'PENDING') AS pending_count,
                COUNT(d.id) FILTER (WHERE d.payment_status = 'OVERDUE') AS overdue_count
            FROM chit_auctions ca
            JOIN chit_groups cg ON ca.chit_group_id = cg.id
            LEFT JOIN monthly_member_dues d ON d.chit_auction_id = ca.id AND d.is_deleted = FALSE
            WHERE ca.organizer_id = $1 AND ca.status = 'FINALIZED' AND ca.is_deleted = FALSE
            GROUP BY ca.id, cg.id
            ORDER BY (COALESCE(SUM(d.remaining_amount), 0) > 0) DESC, ca.auction_month_number DESC
        """
        rows = await self.db.fetch(query, organizer_id)
        return [dict(row) for row in rows]
