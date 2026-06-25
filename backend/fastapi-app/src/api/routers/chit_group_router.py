import asyncpg
from fastapi import APIRouter, Depends, Query, Path as FastAPIPath
from uuid import UUID
from typing import Optional, List, Dict, Any
from datetime import date

from src.api.schemas.chit_group_schema import (
    ChitGroupCreateRequest, ChitGroupUpdateRequest,
    ChitMembershipCreateRequest, ChitMembershipUpdateRequest,
    ChitStatusChangeRequest, ChitGroupResponse, ChitGroupListResponse,
    ChitGroupDetailResponse, ChitMembershipResponse, ChitGroupActivityResponse,
    ChitGroupSummaryResponse, BulkMembershipAllocateRequest, BulkMembershipAllocateResponse
)
from src.api.controllers.chit_group_controller import ChitGroupController
from src.shared.core.database import get_db_session
from src.api.dependencies.auth_dependency import get_current_organizer, get_current_user
from src.api.dependencies.auth_decorator import authorize
from src.api.models.models import User

router = APIRouter(prefix="/api/v1/chit-groups", tags=["chit-groups"])

@router.post("", response_model=ChitGroupResponse, status_code=201)
@authorize(allowed_roles=["ORGANIZER", "ADMIN"])
async def create_chit_group(
    request: ChitGroupCreateRequest,
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = ChitGroupController(db)
    return await controller.create_chit_group(current_user, request)

@router.get("", response_model=ChitGroupListResponse)
@authorize(allowed_roles=["ORGANIZER", "ADMIN"])
async def list_chit_groups(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    start_date_from: Optional[date] = Query(None),
    start_date_to: Optional[date] = Query(None),
    sort_by: str = Query('start_date'),
    sort_order: str = Query('desc'),
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = ChitGroupController(db)
    return await controller.list_chit_groups(
        current_user, page, page_size, search, status, start_date_from, start_date_to, sort_by, sort_order
    )

@router.get("/summary", response_model=ChitGroupSummaryResponse)
@authorize(allowed_roles=["ORGANIZER", "ADMIN"])
async def get_chit_group_summary(
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = ChitGroupController(db)
    return await controller.get_chit_group_summary(current_user)

@router.get("/{chit_group_id}", response_model=ChitGroupDetailResponse)
@authorize(allowed_roles=["ORGANIZER", "ADMIN"])
async def get_chit_group_detail(
    chit_group_id: UUID = FastAPIPath(...),
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = ChitGroupController(db)
    return await controller.get_chit_group_detail(current_user, chit_group_id)

@router.put("/{chit_group_id}", response_model=ChitGroupResponse)
@authorize(allowed_roles=["ORGANIZER", "ADMIN"])
async def update_chit_group(
    chit_group_id: UUID = FastAPIPath(...),
    request: ChitGroupUpdateRequest = ...,
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = ChitGroupController(db)
    return await controller.update_chit_group(current_user, chit_group_id, request)

@router.get("/{chit_group_id}/available-members", response_model=List[Dict[str, Any]])
@authorize(allowed_roles=["ORGANIZER", "ADMIN"])
async def get_available_members(
    chit_group_id: UUID = FastAPIPath(...),
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = ChitGroupController(db)
    return await controller.get_available_members(current_user, chit_group_id)

@router.post("/{chit_group_id}/memberships", response_model=ChitMembershipResponse)
@authorize(allowed_roles=["ORGANIZER", "ADMIN"])
async def allocate_member_shares(
    chit_group_id: UUID = FastAPIPath(...),
    request: ChitMembershipCreateRequest = ...,
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = ChitGroupController(db)
    return await controller.allocate_member_shares(current_user, chit_group_id, request)

@router.put("/{chit_group_id}/memberships/{membership_id}", response_model=ChitMembershipResponse)
@authorize(allowed_roles=["ORGANIZER", "ADMIN"])
async def update_member_shares(
    chit_group_id: UUID = FastAPIPath(...),
    membership_id: UUID = FastAPIPath(...),
    request: ChitMembershipUpdateRequest = ...,
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = ChitGroupController(db)
    return await controller.update_member_shares(current_user, chit_group_id, membership_id, request)

@router.delete("/{chit_group_id}/memberships/{membership_id}", response_model=ChitMembershipResponse)
@authorize(allowed_roles=["ORGANIZER", "ADMIN"])
async def remove_member_from_chit(
    chit_group_id: UUID = FastAPIPath(...),
    membership_id: UUID = FastAPIPath(...),
    remarks: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = ChitGroupController(db)
    return await controller.remove_member_from_chit(current_user, chit_group_id, membership_id, remarks)

@router.post("/{chit_group_id}/status", response_model=ChitGroupResponse)
@authorize(allowed_roles=["ORGANIZER", "ADMIN"])
async def change_chit_status(
    chit_group_id: UUID = FastAPIPath(...),
    request: ChitStatusChangeRequest = ...,
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = ChitGroupController(db)
    return await controller.change_chit_status(current_user, chit_group_id, request)

@router.get("/{chit_group_id}/activity", response_model=List[ChitGroupActivityResponse])
@authorize(allowed_roles=["ORGANIZER", "ADMIN"])
async def get_chit_group_activity(
    chit_group_id: UUID = FastAPIPath(...),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = ChitGroupController(db)
    return await controller.get_chit_group_activity(current_user, chit_group_id, page, page_size)

@router.post("/{chit_group_id}/memberships/bulk-allocate", response_model=BulkMembershipAllocateResponse)
@authorize(allowed_roles=["ORGANIZER", "ADMIN"])
async def bulk_allocate_equal_shares(
    chit_group_id: UUID = FastAPIPath(...),
    request: BulkMembershipAllocateRequest = ...,
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = ChitGroupController(db)
    return await controller.bulk_allocate_equal_shares(current_user, chit_group_id, request)

