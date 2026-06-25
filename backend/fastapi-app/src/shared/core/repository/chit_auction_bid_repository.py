from uuid import UUID
import uuid
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class ChitAuctionBidRepository:
    def __init__(self, db_object):
        self.db = db_object

    async def get_bid_by_auction_and_membership(self, auction_id: UUID, membership_id: UUID) -> Optional[dict]:
        """Check if a membership has already placed an active bid in this auction."""
        query = """
            SELECT * FROM chit_auction_bids
            WHERE chit_auction_id = $1 AND membership_id = $2 AND status = 'ACTIVE' AND is_deleted = FALSE
        """
        row = await self.db.fetchrow(query, auction_id, membership_id)
        return dict(row) if row else None

    async def create_bid(self, data: dict, created_by: UUID) -> dict:
        bid_id = uuid.uuid4()
        now = datetime.utcnow()
        query = """
            INSERT INTO chit_auction_bids (
                id, organizer_id, chit_auction_id, chit_group_id,
                membership_id, member_id, bid_discount_amount, remarks,
                bid_time, status, created_at, created_by, is_deleted, version
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, 'ACTIVE', $9, $10, FALSE, 1)
            RETURNING *
        """
        row = await self.db.fetchrow(
            query,
            bid_id,
            data["organizer_id"],
            data["chit_auction_id"],
            data["chit_group_id"],
            data["membership_id"],
            data["member_id"],
            Decimal(str(data["bid_discount_amount"])),
            data.get("remarks"),
            now,
            created_by,
        )
        return dict(row)

    async def list_bids_for_auction(self, auction_id: UUID) -> List[dict]:
        """Return all bids (with member details) for display, ordered by discount DESC."""
        query = """
            SELECT
                b.*,
                m.full_name AS member_name,
                m.member_code,
                cm.share_count
            FROM chit_auction_bids b
            JOIN members m ON m.id = b.member_id
            JOIN chit_memberships cm ON cm.id = b.membership_id
            WHERE b.chit_auction_id = $1 AND b.is_deleted = FALSE
            ORDER BY b.bid_discount_amount DESC, b.bid_time ASC
        """
        rows = await self.db.fetch(query, auction_id)
        return [dict(row) for row in rows]

    async def lock_active_bids_for_auction(self, auction_id: UUID) -> List[dict]:
        """Pessimistic lock on active bids during finalization — must be in transaction."""
        query = """
            SELECT b.*, cm.share_count
            FROM chit_auction_bids b
            JOIN chit_memberships cm ON cm.id = b.membership_id
            WHERE b.chit_auction_id = $1 AND b.status = 'ACTIVE' AND b.is_deleted = FALSE
            ORDER BY b.bid_discount_amount DESC, b.bid_time ASC
            FOR UPDATE OF b NOWAIT
        """
        rows = await self.db.fetch(query, auction_id)
        return [dict(row) for row in rows]
