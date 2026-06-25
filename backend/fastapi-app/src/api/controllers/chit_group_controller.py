import asyncpg
from uuid import UUID
from typing import Optional
from src.shared.core.services.chit_group_service import ChitGroupService
from src.shared.core.services.chit_membership_service import ChitMembershipService
from src.api.schemas.chit_group_schema import (
    ChitGroupCreateRequest, ChitGroupUpdateRequest,
    ChitMembershipCreateRequest, ChitMembershipUpdateRequest,
    ChitStatusChangeRequest, BulkMembershipAllocateRequest
)
from src.api.models.models import User
from datetime import date

class ChitGroupController:
    def __init__(self, db_object: asyncpg.Connection):
        self.db_object = db_object
        self.chit_service = ChitGroupService(db_object)
        self.membership_service = ChitMembershipService(db_object)


    async def create_chit_group(self, current_user: User, request: ChitGroupCreateRequest):
        return await self.chit_service.create_chit_group(current_user, request)

    async def list_chit_groups(
        self,
        current_user: User,
        page: int,
        page_size: int,
        search: Optional[str],
        status: Optional[str],
        start_date_from: Optional[date],
        start_date_to: Optional[date],
        sort_by: str,
        sort_order: str
    ):
        return await self.chit_service.list_chit_groups(
            current_user, page, page_size, search, status, start_date_from, start_date_to, sort_by, sort_order
        )

    async def get_chit_group_detail(self, current_user: User, chit_group_id: UUID):
        return await self.chit_service.get_chit_group_detail(current_user, chit_group_id)

    async def update_chit_group(self, current_user: User, chit_group_id: UUID, request: ChitGroupUpdateRequest):
        return await self.chit_service.update_chit_group(current_user, chit_group_id, request)

    async def allocate_member_shares(self, current_user: User, chit_group_id: UUID, request: ChitMembershipCreateRequest):
        return await self.chit_service.allocate_member_shares(current_user, chit_group_id, request)

    async def update_member_shares(self, current_user: User, chit_group_id: UUID, membership_id: UUID, request: ChitMembershipUpdateRequest):
        return await self.chit_service.update_member_shares(current_user, chit_group_id, membership_id, request)

    async def remove_member_from_chit(self, current_user: User, chit_group_id: UUID, membership_id: UUID, remarks: Optional[str]):
        return await self.chit_service.remove_member_from_chit(current_user, chit_group_id, membership_id, remarks)

    async def change_chit_status(self, current_user: User, chit_group_id: UUID, request: ChitStatusChangeRequest):
        return await self.chit_service.change_chit_status(current_user, chit_group_id, request)

    async def get_chit_group_activity(self, current_user: User, chit_group_id: UUID, page: int, page_size: int):
        return await self.chit_service.get_chit_group_activity(current_user, chit_group_id, page, page_size)

    async def get_chit_group_summary(self, current_user: User):
        return await self.chit_service.get_chit_group_summary(current_user)

    async def get_available_members(self, current_user: User, chit_group_id: UUID):
        return await self.chit_service.get_available_members(current_user, chit_group_id)

    async def bulk_allocate_equal_shares(self, current_user: User, chit_group_id: UUID, request: BulkMembershipAllocateRequest):
        return await self.membership_service.bulk_allocate_equal_shares(self.db_object, chit_group_id, request, current_user)

