import uuid
from uuid import UUID
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

class ChitPaymentReceiptRepository:
    def __init__(self, db_object):
        self.db = db_object

    async def create_receipt(self, receipt_data: dict, created_by: UUID) -> dict:
        now = datetime.utcnow()
        receipt_id = uuid.uuid4()
        
        query = """
            INSERT INTO chit_payment_receipts (
                id, organizer_id, chit_group_id, chit_auction_id,
                monthly_member_due_id, membership_id, member_id,
                receipt_number, payment_date, payment_amount,
                payment_method, transaction_reference, collected_by_user_id,
                remarks, status, client_request_id,
                created_at, created_by, is_deleted, version
            ) VALUES (
                $1, $2, $3, $4,
                $5, $6, $7,
                $8, $9, $10,
                $11, $12, $13,
                $14, $15, $16,
                $17, $18, FALSE, 1
            ) RETURNING *
        """
        
        row = await self.db.fetchrow(
            query,
            receipt_id,
            receipt_data["organizer_id"],
            receipt_data["chit_group_id"],
            receipt_data["chit_auction_id"],
            receipt_data["monthly_member_due_id"],
            receipt_data["membership_id"],
            receipt_data["member_id"],
            receipt_data["receipt_number"],
            receipt_data.get("payment_date", now),
            Decimal(str(receipt_data["payment_amount"])),
            receipt_data.get("payment_method", "CASH"),
            receipt_data.get("transaction_reference"),
            receipt_data.get("collected_by_user_id", created_by),
            receipt_data.get("remarks"),
            "SUCCESS",
            receipt_data.get("client_request_id"),
            now,
            created_by
        )
        return dict(row) if row else None

    async def get_receipt_by_id(self, receipt_id: UUID, organizer_id: UUID) -> Optional[dict]:
        query = """
            SELECT * FROM chit_payment_receipts
            WHERE id = $1 AND organizer_id = $2 AND is_deleted = FALSE
        """
        row = await self.db.fetchrow(query, receipt_id, organizer_id)
        return dict(row) if row else None

    async def get_receipt_by_client_request_id(self, client_request_id: str, organizer_id: UUID) -> Optional[dict]:
        query = """
            SELECT * FROM chit_payment_receipts
            WHERE client_request_id = $1 AND organizer_id = $2 AND is_deleted = FALSE
        """
        row = await self.db.fetchrow(query, client_request_id, organizer_id)
        return dict(row) if row else None

    async def list_receipts_by_due(self, due_id: UUID, organizer_id: UUID) -> List[dict]:
        query = """
            SELECT r.*, u.mobile as collected_by_user_mobile
            FROM chit_payment_receipts r
            LEFT JOIN users u ON r.collected_by_user_id = u.id
            WHERE r.monthly_member_due_id = $1 AND r.organizer_id = $2 AND r.is_deleted = FALSE
            ORDER BY r.payment_date DESC
        """
        rows = await self.db.fetch(query, due_id, organizer_id)
        return [dict(row) for row in rows]

    async def get_receipt_for_update(self, receipt_id: UUID, organizer_id: UUID) -> Optional[dict]:
        query = """
            SELECT * FROM chit_payment_receipts
            WHERE id = $1 AND organizer_id = $2 AND is_deleted = FALSE
            FOR UPDATE
        """
        row = await self.db.fetchrow(query, receipt_id, organizer_id)
        return dict(row) if row else None

    async def reverse_receipt(self, receipt_id: UUID, organizer_id: UUID, reversal_reason: str, user_id: UUID) -> dict:
        now = datetime.utcnow()
        query = """
            UPDATE chit_payment_receipts
            SET status = 'REVERSED',
                reversal_reason = $3,
                reversed_at = $4,
                reversed_by_user_id = $5,
                updated_at = $4,
                updated_by = $5,
                version = version + 1
            WHERE id = $1 AND organizer_id = $2 AND status = 'SUCCESS'
            RETURNING *
        """
        row = await self.db.fetchrow(query, receipt_id, organizer_id, reversal_reason, now, user_id)
        return dict(row) if row else None
