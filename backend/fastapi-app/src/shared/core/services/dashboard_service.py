import asyncpg
from uuid import UUID
from fastapi import HTTPException
from src.shared.core.repository.organizer_repository import OrganizerRepository
from src.shared.core.repository.member_repository import MemberRepository
from src.api.models.models import User

class DashboardService:
    def __init__(self, db_object: asyncpg.Connection):
        self.db = db_object
        self.organizer_repo = OrganizerRepository(db_object)
        self.member_repo = MemberRepository(db_object)

    async def get_summary(self, current_user: User):
        if current_user.role != "ORGANIZER" or not current_user.organizer_id:
            raise HTTPException(status_code=403, detail="Only organizers can access the dashboard summary")

        org = await self.organizer_repo.get_organizer_by_id(current_user.organizer_id)
        if not org:
            raise HTTPException(status_code=404, detail="Organizer not found")

        # Get actual total member count
        member_summary = await self.member_repo.get_member_summary(current_user.organizer_id)
        total_members = member_summary.get("total_members", 0)

        # Get active chits count
        active_chits = await self.db.fetchval(
            "SELECT COUNT(id) FROM chit_groups WHERE organizer_id = $1 AND status = 'ACTIVE' AND is_deleted = FALSE",
            current_user.organizer_id
        ) or 0

        # Collections due today
        collections_due_today = await self.db.fetchval(
            "SELECT COALESCE(SUM(net_payable_amount), 0) FROM monthly_member_dues WHERE organizer_id = $1 AND due_date = CURRENT_DATE",
            current_user.organizer_id
        ) or 0.0

        # Collections received today
        collections_received_today = await self.db.fetchval(
            "SELECT COALESCE(SUM(payment_amount), 0) FROM chit_payment_receipts WHERE organizer_id = $1 AND DATE(payment_date) = CURRENT_DATE AND status = 'SUCCESS'",
            current_user.organizer_id
        ) or 0.0

        # Pending amount (past due and due today)
        pending_amount = await self.db.fetchval(
            "SELECT COALESCE(SUM(remaining_amount), 0) FROM monthly_member_dues WHERE organizer_id = $1 AND payment_status != 'PAID' AND due_date <= CURRENT_DATE",
            current_user.organizer_id
        ) or 0.0

        # Auctions today
        auctions_today = await self.db.fetchval(
            "SELECT COUNT(id) FROM chit_auctions WHERE organizer_id = $1 AND DATE(auction_date) = CURRENT_DATE AND status IN ('SCHEDULED', 'IN_PROGRESS', 'COMPLETED')",
            current_user.organizer_id
        ) or 0

        return {
            "organizer_name": org.name,
            "active_chits": active_chits,
            "total_members": total_members,
            "collections_due_today": float(collections_due_today),
            "collections_received_today": float(collections_received_today),
            "pending_amount": float(pending_amount),
            "auctions_today": auctions_today
        }

