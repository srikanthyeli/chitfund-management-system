import asyncpg
from uuid import UUID
from fastapi import HTTPException
from src.api.models.models import User

class DashboardService:
    def __init__(self, db_object: asyncpg.Connection):
        self.db = db_object

    async def get_summary(self, current_user: User):
        if current_user.role != "ORGANIZER" or not current_user.organizer_id:
            raise HTTPException(status_code=403, detail="Only organizers can access the dashboard summary")

        organizer_id = current_user.organizer_id

        summary_row = await self.db.fetchrow(
            """
            SELECT
                o.name AS organizer_name,
                COALESCE((SELECT COUNT(*) FROM chit_groups WHERE organizer_id = $1 AND status = 'ACTIVE' AND is_deleted = FALSE), 0) AS active_chits,
                COALESCE((SELECT COUNT(*) FROM members WHERE organizer_id = $1 AND is_deleted = FALSE), 0) AS total_members,
                COALESCE((SELECT SUM(net_payable_amount) FROM monthly_member_dues WHERE organizer_id = $1 AND due_date = CURRENT_DATE), 0) AS collections_due_today,
                COALESCE((SELECT SUM(payment_amount) FROM chit_payment_receipts WHERE organizer_id = $1 AND DATE(payment_date) = CURRENT_DATE AND status = 'SUCCESS'), 0) AS collections_received_today,
                COALESCE((SELECT SUM(remaining_amount) FROM monthly_member_dues WHERE organizer_id = $1 AND payment_status != 'PAID' AND due_date <= CURRENT_DATE), 0) AS pending_amount,
                COALESCE((SELECT COUNT(*) FROM chit_auctions WHERE organizer_id = $1 AND DATE(auction_date) = CURRENT_DATE AND status IN ('SCHEDULED', 'IN_PROGRESS', 'COMPLETED')), 0) AS auctions_today
            FROM organizers o
            WHERE o.id = $1 AND o.is_deleted = FALSE
            """,
            organizer_id,
        )

        if not summary_row:
            raise HTTPException(status_code=404, detail="Organizer not found")

        return {
            "organizer_name": summary_row["organizer_name"],
            "active_chits": summary_row["active_chits"],
            "total_members": summary_row["total_members"],
            "collections_due_today": float(summary_row["collections_due_today"]),
            "collections_received_today": float(summary_row["collections_received_today"]),
            "pending_amount": float(summary_row["pending_amount"]),
            "auctions_today": summary_row["auctions_today"]
        }

