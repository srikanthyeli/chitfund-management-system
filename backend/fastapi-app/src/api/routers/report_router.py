import asyncpg
from fastapi import APIRouter, Depends, Query
from uuid import UUID
from typing import Optional
from datetime import date

from src.api.schemas.reports_schemas import ReportResponse, DashboardMetricsResponse
from src.api.controllers.report_controller import ReportController
from src.shared.core.database import get_db_session
from src.api.dependencies.auth_dependency import get_current_user
from src.api.dependencies.auth_decorator import authorize
from src.api.models.models import User

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])

@router.get("/dashboard", response_model=DashboardMetricsResponse)
@authorize(allowed_roles=["ORGANIZER", "ADMIN"])
async def get_dashboard_metrics(
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = ReportController(db)
    return await controller.get_dashboard_metrics(current_user)

@router.get("/collections", response_model=ReportResponse)
@authorize(allowed_roles=["ORGANIZER", "ADMIN"])
async def get_collections_report(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None),
    member_id: Optional[UUID] = Query(None),
    chit_group_id: Optional[UUID] = Query(None),
    export: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = ReportController(db)
    return await controller.get_collections_report(
        current_user, page, limit, date_from, date_to, month, year, member_id, chit_group_id, export
    )

@router.get("/pending-collections", response_model=ReportResponse)
@authorize(allowed_roles=["ORGANIZER", "ADMIN"])
async def get_pending_collections_report(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    export: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = ReportController(db)
    return await controller.get_pending_collections_report(current_user, page, limit, export)

@router.get("/auctions", response_model=ReportResponse)
@authorize(allowed_roles=["ORGANIZER", "ADMIN"])
async def get_auction_report(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    export: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = ReportController(db)
    return await controller.get_auction_report(current_user, page, limit, export)

@router.get("/winner-payouts", response_model=ReportResponse)
@authorize(allowed_roles=["ORGANIZER", "ADMIN"])
async def get_winner_payout_report(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    export: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = ReportController(db)
    return await controller.get_winner_payout_report(current_user, page, limit, export)

@router.get("/member-financial", response_model=ReportResponse)
@authorize(allowed_roles=["ORGANIZER", "ADMIN"])
async def get_member_financial_report(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    export: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = ReportController(db)
    return await controller.get_member_financial_report(current_user, page, limit, export)

@router.get("/organizer-financial", response_model=ReportResponse)
@authorize(allowed_roles=["ORGANIZER", "ADMIN"])
async def get_organizer_financial_report(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    export: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = ReportController(db)
    return await controller.get_organizer_financial_report(current_user, page, limit, export)

@router.get("/chit-performance", response_model=ReportResponse)
@authorize(allowed_roles=["ORGANIZER", "ADMIN"])
async def get_chit_performance_report(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    export: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = ReportController(db)
    return await controller.get_chit_performance_report(current_user, page, limit, export)
