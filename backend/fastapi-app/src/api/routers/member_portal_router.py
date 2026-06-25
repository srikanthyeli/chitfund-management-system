from fastapi import APIRouter, Depends, Query, Path as FastAPIPath
from uuid import UUID
from typing import List
import asyncpg

from src.api.models.models import User
from src.shared.core.database import get_db_session
from src.api.dependencies.auth_dependency import get_current_member
from src.api.controllers.member_portal_controller import MemberPortalController
from src.api.schemas.member_portal_schema import (
    MemberDashboardResponse, ChitSummaryResponse, NotificationListResponse
)

router = APIRouter(prefix="/api/v1/member-portal", tags=["member_portal"])

@router.get("/dashboard", response_model=MemberDashboardResponse)
async def get_dashboard(
    current_user: User = Depends(get_current_member),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = MemberPortalController(db)
    return await controller.get_dashboard(current_user)

@router.get("/chits", response_model=List[ChitSummaryResponse])
async def list_chits(
    current_user: User = Depends(get_current_member),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = MemberPortalController(db)
    return await controller.list_chits(current_user)

@router.get("/notifications", response_model=NotificationListResponse)
async def get_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_member),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = MemberPortalController(db)
    return await controller.get_notifications(current_user, page, page_size)
