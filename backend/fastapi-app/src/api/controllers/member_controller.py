import asyncpg
from uuid import UUID
from typing import Optional
from src.shared.core.services.member_service import MemberService
from src.api.schemas.member_schema import (
    MemberCreateRequest, MemberUpdateRequest, MemberStatusRequest, MemberMobileUpdateRequest
)
from src.api.models.models import User

class MemberController:
    def __init__(self, db_object: asyncpg.Connection):
        self.db_object = db_object
        self.member_service = MemberService(db_object)

    async def create_member(self, current_user: User, request: MemberCreateRequest):
        return await self.member_service.create_member(current_user, request)

    async def list_members(
        self,
        current_user: User,
        page: int,
        page_size: int,
        search: Optional[str],
        is_active: Optional[bool],
        sort_by: str,
        sort_order: str
    ):
        return await self.member_service.list_members(
            current_user, page, page_size, search, is_active, sort_by, sort_order
        )

    async def get_member(self, current_user: User, member_id: UUID):
        return await self.member_service.get_member(current_user, member_id)

    async def update_member(self, current_user: User, member_id: UUID, request: MemberUpdateRequest):
        return await self.member_service.update_member(current_user, member_id, request)

    async def update_member_mobile(self, current_user: User, member_id: UUID, request: MemberMobileUpdateRequest):
        return await self.member_service.update_member_mobile(current_user, member_id, request)

    async def update_member_status(self, current_user: User, member_id: UUID, request: MemberStatusRequest):
        return await self.member_service.update_member_status(current_user, member_id, request)

    async def get_member_activity(self, current_user: User, member_id: UUID, page: int, page_size: int):
        return await self.member_service.get_member_activity(current_user, member_id, page, page_size)

    async def get_member_summary(self, current_user: User):
        return await self.member_service.get_member_summary(current_user)
