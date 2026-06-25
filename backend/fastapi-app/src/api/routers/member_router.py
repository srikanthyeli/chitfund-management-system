import asyncpg
from fastapi import APIRouter, Depends, Query, Path as FastAPIPath
from uuid import UUID
from typing import Optional, List

from src.api.schemas.member_schema import (
    MemberCreateRequest, MemberUpdateRequest, MemberStatusRequest, MemberMobileUpdateRequest,
    MemberResponse, MemberListResponse, MemberActivityResponse, MemberSummaryResponse
)
from src.api.controllers.member_controller import MemberController
from src.shared.core.database import get_db_session
from src.api.dependencies.auth_dependency import get_current_organizer
from src.api.models.models import User

router = APIRouter(prefix="/api/v1/members", tags=["members"])

@router.post("", response_model=MemberResponse, status_code=201)
async def create_member(
    request: MemberCreateRequest,
    current_user: User = Depends(get_current_organizer),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = MemberController(db)
    return await controller.create_member(current_user, request)

@router.get("", response_model=MemberListResponse)
async def list_members(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    sort_by: str = Query('created_at'),
    sort_order: str = Query('desc'),
    current_user: User = Depends(get_current_organizer),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = MemberController(db)
    return await controller.list_members(
        current_user, page, page_size, search, is_active, sort_by, sort_order
    )

@router.get("/summary", response_model=MemberSummaryResponse)
async def get_member_summary(
    current_user: User = Depends(get_current_organizer),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = MemberController(db)
    return await controller.get_member_summary(current_user)

@router.get("/{member_id}", response_model=MemberResponse)
async def get_member(
    member_id: UUID = FastAPIPath(...),
    current_user: User = Depends(get_current_organizer),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = MemberController(db)
    return await controller.get_member(current_user, member_id)

@router.put("/{member_id}", response_model=MemberResponse)
async def update_member(
    member_id: UUID = FastAPIPath(...),
    request: MemberUpdateRequest = ...,
    current_user: User = Depends(get_current_organizer),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = MemberController(db)
    return await controller.update_member(current_user, member_id, request)

@router.patch("/{member_id}/mobile", response_model=MemberResponse)
async def update_member_mobile(
    member_id: UUID = FastAPIPath(...),
    request: MemberMobileUpdateRequest = ...,
    current_user: User = Depends(get_current_organizer),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = MemberController(db)
    return await controller.update_member_mobile(current_user, member_id, request)

@router.patch("/{member_id}/status", response_model=MemberResponse)
async def update_member_status(
    member_id: UUID = FastAPIPath(...),
    request: MemberStatusRequest = ...,
    current_user: User = Depends(get_current_organizer),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = MemberController(db)
    return await controller.update_member_status(current_user, member_id, request)

@router.get("/{member_id}/activity", response_model=List[MemberActivityResponse])
async def get_member_activity(
    member_id: UUID = FastAPIPath(...),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_organizer),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = MemberController(db)
    return await controller.get_member_activity(current_user, member_id, page, page_size)
