from uuid import UUID
import uuid
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class ChitWinnerPayoutRepository:
    def __init__(self, db_object):
        self.db = db_object

    async def get_payout_by_client_request_id(self, client_request_id: str, organizer_id: UUID) -> Optional[dict]:
        query = """
            SELECT * FROM chit_winner_payouts
            WHERE client_request_id = $1 AND organizer_id = $2
        """
        row = await self.db.fetchrow(query, client_request_id, organizer_id)
        return dict(row) if row else None

    async def get_active_payout_by_group_and_month(self, chit_group_id: UUID, month_number: int, organizer_id: UUID) -> Optional[dict]:
        query = """
            SELECT * FROM chit_winner_payouts
            WHERE chit_group_id = $1 AND month_number = $2 AND organizer_id = $3 AND status NOT IN ('CANCELLED', 'REVERSED')
        """
        row = await self.db.fetchrow(query, chit_group_id, month_number, organizer_id)
        return dict(row) if row else None

    async def create_payout(self, data: dict, created_by: UUID) -> dict:
        now = datetime.utcnow()
        payout_id = uuid.uuid4()
        query = """
            INSERT INTO chit_winner_payouts (
                id, organizer_id, chit_group_id, chit_auction_id,
                winner_membership_id, winner_member_id, month_number,
                gross_chit_amount, winning_bid_discount_amount, maintenance_charge_amount, payout_amount,
                collection_expected_amount, collection_received_amount, collection_pending_amount,
                organizer_contribution_amount, payout_source,
                payment_method, transaction_reference, payout_date, remarks,
                payout_receipt_number, status, client_request_id,
                created_at, created_by, is_deleted, version
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22, $23, $24, $25, FALSE, 1
            ) RETURNING *
        """
        row = await self.db.fetchrow(
            query,
            payout_id,
            data["organizer_id"],
            data["chit_group_id"],
            data["chit_auction_id"],
            data["winner_membership_id"],
            data["winner_member_id"],
            data["month_number"],
            Decimal(str(data["gross_chit_amount"])),
            Decimal(str(data["winning_bid_discount_amount"])),
            Decimal(str(data["maintenance_charge_amount"])),
            Decimal(str(data["payout_amount"])),
            Decimal(str(data.get("collection_expected_amount", 0))),
            Decimal(str(data.get("collection_received_amount", 0))),
            Decimal(str(data.get("collection_pending_amount", 0))),
            Decimal(str(data.get("organizer_contribution_amount", 0))),
            data.get("payout_source", "COLLECTION_ONLY"),
            data.get("payment_method", "BANK_TRANSFER"),
            data.get("transaction_reference"),
            data.get("payout_date"),
            data.get("remarks"),
            data.get("payout_receipt_number", f"DRAFT-{uuid.uuid4().hex[:8]}"),
            data.get("status", "DRAFT"),
            data.get("client_request_id"),
            now,
            created_by
        )
        return dict(row)

    async def get_payout_for_update(self, payout_id: UUID, organizer_id: UUID) -> Optional[dict]:
        query = """
            SELECT * FROM chit_winner_payouts
            WHERE id = $1 AND organizer_id = $2
            FOR UPDATE
        """
        row = await self.db.fetchrow(query, payout_id, organizer_id)
        return dict(row) if row else None

    async def get_payout_by_id(self, payout_id: UUID, organizer_id: UUID) -> Optional[dict]:
        query = """
            SELECT p.*, cg.chit_name, m.full_name AS winner_name, m.mobile AS winner_phone, m.member_code
            FROM chit_winner_payouts p
            JOIN chit_groups cg ON cg.id = p.chit_group_id
            JOIN members m ON m.id = p.winner_member_id
            WHERE p.id = $1 AND p.organizer_id = $2
        """
        row = await self.db.fetchrow(query, payout_id, organizer_id)
        return dict(row) if row else None

    async def get_payout_public(self, payout_id: UUID) -> Optional[dict]:
        query = """
            SELECT p.*, cg.chit_name, m.full_name AS winner_name, m.mobile AS winner_phone, m.member_code
            FROM chit_winner_payouts p
            JOIN chit_groups cg ON cg.id = p.chit_group_id
            JOIN members m ON m.id = p.winner_member_id
            WHERE p.id = $1
        """
        row = await self.db.fetchrow(query, payout_id)
        return dict(row) if row else None

    async def list_payouts(self, organizer_id: UUID, limit: int = 50, offset: int = 0) -> List[dict]:
        query = """
            SELECT p.*, cg.chit_name, m.full_name AS winner_name
            FROM chit_winner_payouts p
            JOIN chit_groups cg ON cg.id = p.chit_group_id
            JOIN members m ON m.id = p.winner_member_id
            WHERE p.organizer_id = $1
            ORDER BY p.created_at DESC
            LIMIT $2 OFFSET $3
        """
        rows = await self.db.fetch(query, organizer_id, limit, offset)
        return [dict(row) for row in rows]

    async def update_payout(self, payout_id: UUID, organizer_id: UUID, updates: dict, updated_by: UUID) -> Optional[dict]:
        if not updates:
            return await self.get_payout_by_id(payout_id, organizer_id)
        
        set_clauses = []
        values = []
        for i, (k, v) in enumerate(updates.items(), start=1):
            set_clauses.append(f"{k} = ${i}")
            values.append(v)
            
        values.extend([datetime.utcnow(), updated_by, payout_id, organizer_id])
        idx = len(updates)
        set_clauses.extend([
            f"updated_at = ${idx + 1}",
            f"updated_by = ${idx + 2}",
            "version = version + 1"
        ])
        
        query = f"""
            UPDATE chit_winner_payouts
            SET {", ".join(set_clauses)}
            WHERE id = ${idx + 3} AND organizer_id = ${idx + 4}
            RETURNING *
        """
        row = await self.db.fetchrow(query, *values)
        return dict(row) if row else None

    async def reverse_payout(self, payout_id: UUID, organizer_id: UUID, reversal_reason: str, reversed_by: UUID) -> Optional[dict]:
        now = datetime.utcnow()
        query = """
            UPDATE chit_winner_payouts
            SET status = 'REVERSED', reversal_reason = $1, reversed_at = $2, reversed_by_user_id = $3,
                updated_at = $2, updated_by = $3, version = version + 1
            WHERE id = $4 AND organizer_id = $5 AND status IN ('PAID', 'COMPLETED')
            RETURNING *
        """
        row = await self.db.fetchrow(query, reversal_reason, now, reversed_by, payout_id, organizer_id)
        return dict(row) if row else None

    async def list_member_payouts(self, member_id: UUID, organizer_id: UUID) -> List[dict]:
        query = """
            SELECT p.*, cg.chit_name
            FROM chit_winner_payouts p
            JOIN chit_groups cg ON cg.id = p.chit_group_id
            WHERE p.winner_member_id = $1 AND p.organizer_id = $2 AND p.status IN ('PAID', 'WINNER_CONFIRMED')
            ORDER BY p.created_at DESC
        """
        rows = await self.db.fetch(query, member_id, organizer_id)
        return [dict(row) for row in rows]

class ChitWinnerPayoutActivityLogRepository:
    def __init__(self, db_object):
        self.db = db_object

    async def create_log(self, organizer_id: UUID, winner_payout_id: UUID, action_type: str, performed_by_user_id: UUID, old_values: dict = None, new_values: dict = None, remarks: str = None) -> dict:
        query = """
            INSERT INTO chit_winner_payout_activity_logs (
                id, organizer_id, winner_payout_id, action_type, old_values, new_values, remarks, performed_by_user_id, created_at
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9
            ) RETURNING *
        """
        import json
        row = await self.db.fetchrow(
            query,
            uuid.uuid4(),
            organizer_id,
            winner_payout_id,
            action_type,
            json.dumps(old_values) if old_values else None,
            json.dumps(new_values) if new_values else None,
            remarks,
            performed_by_user_id,
            datetime.utcnow()
        )
        return dict(row)
