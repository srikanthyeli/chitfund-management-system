import uuid
from uuid import UUID
from datetime import datetime

class PaymentReceiptSequenceRepository:
    def __init__(self, db_object):
        self.db = db_object

    async def get_next_sequence(self, organizer_id: UUID, receipt_prefix: str) -> int:
        """
        Gets the next sequence number for a given prefix, inserting a new row if it doesn't exist,
        and locking the row for update to prevent concurrent race conditions.
        """
        now = datetime.utcnow()
        
        # Try to insert if not exists (upsert pattern)
        insert_query = """
            INSERT INTO payment_receipt_sequences (id, organizer_id, receipt_prefix, current_sequence, created_at)
            VALUES ($1, $2, $3, 0, $4)
            ON CONFLICT (organizer_id, receipt_prefix) DO NOTHING
        """
        await self.db.execute(insert_query, uuid.uuid4(), organizer_id, receipt_prefix, now)

        # Now select for update and increment
        update_query = """
            UPDATE payment_receipt_sequences
            SET current_sequence = current_sequence + 1, updated_at = $3
            WHERE organizer_id = $1 AND receipt_prefix = $2
            RETURNING current_sequence
        """
        row = await self.db.fetchrow(update_query, organizer_id, receipt_prefix, now)
        return row["current_sequence"] if row else 1
