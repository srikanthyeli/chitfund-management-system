from uuid import UUID
import asyncpg
from typing import Optional
from datetime import date

from src.api.models.models import User
from src.shared.core.repository.reports_repository import ReportsRepository
from src.shared.core.services.report_service import ReportService
from src.api.schemas.reports_schemas import ReportResponse, DashboardMetricsResponse

class ReportController:
    def __init__(self, db: asyncpg.Connection):
        self.db = db
        self.repo = ReportsRepository(db)
        self.service = ReportService(self.repo)
        
    def _get_tenant_id(self, current_user: User) -> UUID:
        return current_user.organizer_id

    async def get_dashboard_metrics(self, current_user: User) -> DashboardMetricsResponse:
        tenant_id = self._get_tenant_id(current_user)
        return await self.service.get_dashboard_metrics(tenant_id)

    async def get_collections_report(
        self, current_user: User, page: int, limit: int,
        date_from: Optional[date] = None, date_to: Optional[date] = None,
        month: Optional[int] = None, year: Optional[int] = None,
        member_id: Optional[UUID] = None, chit_group_id: Optional[UUID] = None,
        export: bool = False
    ) -> ReportResponse:
        tenant_id = self._get_tenant_id(current_user)
        return await self.service.get_collections_report(
            tenant_id, page, limit, date_from, date_to, month, year, member_id, chit_group_id, export
        )

    async def get_pending_collections_report(
        self, current_user: User, page: int, limit: int, export: bool = False
    ) -> ReportResponse:
        tenant_id = self._get_tenant_id(current_user)
        return await self.service.get_pending_collections_report(tenant_id, page, limit, export)

    async def get_auction_report(
        self, current_user: User, page: int, limit: int, export: bool = False
    ) -> ReportResponse:
        tenant_id = self._get_tenant_id(current_user)
        return await self.service.get_auction_report(tenant_id, page, limit, export)

    async def get_winner_payout_report(
        self, current_user: User, page: int, limit: int, export: bool = False
    ) -> ReportResponse:
        tenant_id = self._get_tenant_id(current_user)
        return await self.service.get_winner_payout_report(tenant_id, page, limit, export)

    async def get_member_financial_report(
        self, current_user: User, page: int, limit: int, export: bool = False
    ) -> ReportResponse:
        tenant_id = self._get_tenant_id(current_user)
        return await self.service.get_member_financial_report(tenant_id, page, limit, export)

    async def get_organizer_financial_report(
        self, current_user: User, page: int, limit: int, export: bool = False
    ) -> ReportResponse:
        tenant_id = self._get_tenant_id(current_user)
        return await self.service.get_organizer_financial_report(tenant_id, page, limit, export)

    async def get_chit_performance_report(
        self, current_user: User, page: int, limit: int, export: bool = False
    ) -> ReportResponse:
        tenant_id = self._get_tenant_id(current_user)
        return await self.service.get_chit_performance_report(tenant_id, page, limit, export)
