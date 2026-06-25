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

        return {
            "organizer_name": org.name,
            "active_chits": 0,
            "total_members": total_members,
            "collections_due_today": 0,
            "collections_received_today": 0,
            "pending_amount": 0.0,
            "auctions_today": 0
        }

