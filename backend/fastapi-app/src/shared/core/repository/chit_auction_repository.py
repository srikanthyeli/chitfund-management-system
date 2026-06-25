from uuid import UUID
import uuid
from typing import Optional, List, Tuple
from datetime import datetime, date
from decimal import Decimal


class ChitAuctionRepository:
    def __init__(self, db_object):
        self.db = db_object

    async def get_auction_by_chit_and_month(self, chit_group_id: UUID, month_number: int) -> Optional[dict]:
        query = """
            SELECT * FROM chit_auctions
            WHERE chit_group_id = $1 AND auction_month_number = $2 AND is_deleted = FALSE
        """
        row = await self.db.fetchrow(query, chit_group_id, month_number)
        return dict(row) if row else None

    async def create_auction(self, data: dict, created_by: UUID) -> dict:
        auction_id = uuid.uuid4()
        now = datetime.utcnow()
        query = """
            INSERT INTO chit_auctions (
                id, organizer_id, chit_group_id, auction_month_number, auction_date,
                status, gross_chit_amount, maintenance_charge, maximum_bid_discount,
                notes, created_at, created_by, is_deleted, version
            )
            VALUES ($1, $2, $3, $4, $5, 'OPEN', $6, $7, $8, $9, $10, $11, FALSE, 1)
            RETURNING *
        """
        row = await self.db.fetchrow(
            query,
            auction_id,
            data["organizer_id"],
            data["chit_group_id"],
            data["auction_month_number"],
            data["auction_date"],
            Decimal(str(data["gross_chit_amount"])),
            Decimal(str(data["maintenance_charge"])),
            Decimal(str(data["maximum_bid_discount"])),
            data.get("notes"),
            now,
            created_by,
        )
        return dict(row)

    async def get_auction_by_id(self, auction_id: UUID, organizer_id: UUID) -> Optional[dict]:
        query = """
            SELECT a.*, cg.chit_name, cg.chit_code, cg.monthly_installment_per_share, cg.total_shares
            FROM chit_auctions a
            JOIN chit_groups cg ON cg.id = a.chit_group_id
            WHERE a.id = $1 AND a.organizer_id = $2 AND a.is_deleted = FALSE
        """
        row = await self.db.fetchrow(query, auction_id, organizer_id)
        return dict(row) if row else None

    async def get_auction_by_id_raw(self, auction_id: UUID) -> Optional[dict]:
        """Used internally without organizer scope enforcement (e.g., finalization locking)."""
        query = """
            SELECT * FROM chit_auctions WHERE id = $1 AND is_deleted = FALSE
        """
        row = await self.db.fetchrow(query, auction_id)
        return dict(row) if row else None

    async def lock_auction_for_finalize(self, auction_id: UUID) -> Optional[dict]:
        """Pessimistic lock — must be called inside a transaction."""
        query = """
            SELECT * FROM chit_auctions
            WHERE id = $1 AND is_deleted = FALSE
            FOR UPDATE NOWAIT
        """
        row = await self.db.fetchrow(query, auction_id)
        return dict(row) if row else None

    async def list_auctions_by_chit_group(self, chit_group_id: UUID, organizer_id: UUID) -> List[dict]:
        query = """
            SELECT
                a.*,
                COUNT(b.id) FILTER (WHERE b.status = 'ACTIVE' AND b.is_deleted = FALSE) AS bid_count,
                MAX(b.bid_discount_amount) FILTER (WHERE b.status = 'ACTIVE' AND b.is_deleted = FALSE) AS highest_bid
            FROM chit_auctions a
            LEFT JOIN chit_auction_bids b ON b.chit_auction_id = a.id
            WHERE a.chit_group_id = $1 AND a.organizer_id = $2 AND a.is_deleted = FALSE
            GROUP BY a.id
            ORDER BY a.auction_month_number ASC
        """
        rows = await self.db.fetch(query, chit_group_id, organizer_id)
        return [dict(row) for row in rows]

    async def update_auction_status(self, auction_id: UUID, status: str, updated_by: UUID) -> Optional[dict]:
        query = """
            UPDATE chit_auctions
            SET status = $1, updated_at = $2, updated_by = $3, version = version + 1
            WHERE id = $4 AND is_deleted = FALSE
            RETURNING *
        """
        row = await self.db.fetchrow(query, status, datetime.utcnow(), updated_by, auction_id)
        return dict(row) if row else None

    async def finalize_auction(
        self,
        auction_id: UUID,
        winner_membership_id: UUID,
        winner_member_id: UUID,
        total_discount_amount: Decimal,
        winner_payout_amount: Decimal,
        bonus_per_share: Decimal,
        finalized_by: UUID,
    ) -> Optional[dict]:
        now = datetime.utcnow()
        query = """
            UPDATE chit_auctions
            SET
                status = 'FINALIZED',
                total_discount_amount = $1,
                winner_membership_id = $2,
                winner_member_id = $3,
                winner_payout_amount = $4,
                bonus_per_share = $5,
                finalized_at = $6,
                finalized_by_user_id = $7,
                updated_at = $6,
                updated_by = $7,
                version = version + 1
            WHERE id = $8 AND is_deleted = FALSE
            RETURNING *
        """
        row = await self.db.fetchrow(
            query,
            total_discount_amount,
            winner_membership_id,
            winner_member_id,
            winner_payout_amount,
            bonus_per_share,
            now,
            finalized_by,
            auction_id,
        )
        return dict(row) if row else None
