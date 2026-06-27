from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID
from datetime import date
from math import ceil

from src.shared.core.repository.reports_repository import ReportsRepository
from src.api.schemas.reports_schemas import (
    PaginationMeta,
    ReportResponse,
    DashboardMetricsResponse,
    CollectionReportItem,
    PendingCollectionReportItem,
    AuctionReportItem,
    WinnerPayoutReportItem,
    MemberFinancialReportItem,
    OrganizerFinancialReportItem,
    ChitPerformanceReportItem
)

class ReportService:
    def __init__(self, repo: ReportsRepository):
        self.repo = repo

    def _build_pagination_response(self, items: List[Any], total: int, page: int, limit: int, summary: dict = None) -> ReportResponse:
        page_size = limit if limit > 0 else total
        total_pages = ceil(total / page_size) if page_size > 0 else 1
        return ReportResponse(
            data=items,
            summary=summary or {},
            pagination=PaginationMeta(
                page=page,
                page_size=page_size,
                total_records=total,
                total_pages=total_pages
            )
        )

    async def get_dashboard_metrics(self, tenant_id: UUID) -> DashboardMetricsResponse:
        metrics = await self.repo.get_dashboard_metrics(tenant_id)
        
        # In a real scenario, these chart series would have their own queries grouped by month.
        # For simplicity in this iteration, we return empty or mocked structural data.
        # It can be expanded in the repository if exact trends are needed.
        metrics['monthly_collection_trend'] = []
        metrics['monthly_payout_trend'] = []
        metrics['payment_mode_distribution'] = []
        metrics['collection_success_percentage'] = []
        metrics['monthly_revenue'] = []
        
        return DashboardMetricsResponse(**metrics)

    async def get_collections_report(
        self, tenant_id: UUID, page: int, limit: int,
        date_from: Optional[date] = None, date_to: Optional[date] = None,
        month: Optional[int] = None, year: Optional[int] = None,
        member_id: Optional[UUID] = None, chit_group_id: Optional[UUID] = None,
        export: bool = False
    ) -> ReportResponse:
        actual_limit = 0 if export else limit
        skip = 0 if export else (page - 1) * limit
        
        rows, total = await self.repo.get_collections_report(
            tenant_id, skip, actual_limit, date_from, date_to, month, year, member_id, chit_group_id
        )
        
        items = [CollectionReportItem(**r) for r in rows]
        summary = {"total_amount": sum(item.amount for item in items)}
        return self._build_pagination_response(items, total, page, actual_limit, summary)

    async def get_pending_collections_report(self, tenant_id: UUID, page: int, limit: int, export: bool = False) -> ReportResponse:
        actual_limit = 0 if export else limit
        skip = 0 if export else (page - 1) * limit
        rows, total = await self.repo.get_pending_collections_report(tenant_id, skip, actual_limit)
        items = [PendingCollectionReportItem(**r) for r in rows]
        summary = {"total_pending": sum(item.pending_amount for item in items)}
        return self._build_pagination_response(items, total, page, actual_limit, summary)

    async def get_auction_report(self, tenant_id: UUID, page: int, limit: int, export: bool = False) -> ReportResponse:
        actual_limit = 0 if export else limit
        skip = 0 if export else (page - 1) * limit
        rows, total = await self.repo.get_auction_report(tenant_id, skip, actual_limit)
        items = [AuctionReportItem(**r) for r in rows]
        return self._build_pagination_response(items, total, page, actual_limit)

    async def get_winner_payout_report(self, tenant_id: UUID, page: int, limit: int, export: bool = False) -> ReportResponse:
        actual_limit = 0 if export else limit
        skip = 0 if export else (page - 1) * limit
        rows, total = await self.repo.get_winner_payout_report(tenant_id, skip, actual_limit)
        items = [WinnerPayoutReportItem(**r) for r in rows]
        summary = {"total_net_payout": sum(item.net_amount for item in items)}
        return self._build_pagination_response(items, total, page, actual_limit, summary)

    async def get_member_financial_report(self, tenant_id: UUID, page: int, limit: int, export: bool = False) -> ReportResponse:
        actual_limit = 0 if export else limit
        skip = 0 if export else (page - 1) * limit
        rows, total = await self.repo.get_member_financial_report(tenant_id, skip, actual_limit)
        items = [MemberFinancialReportItem(**r) for r in rows]
        return self._build_pagination_response(items, total, page, actual_limit)

    async def get_organizer_financial_report(self, tenant_id: UUID, page: int, limit: int, export: bool = False) -> ReportResponse:
        actual_limit = 0 if export else limit
        skip = 0 if export else (page - 1) * limit
        rows, total = await self.repo.get_organizer_financial_report(tenant_id, skip, actual_limit)
        items = [OrganizerFinancialReportItem(**r) for r in rows]
        return self._build_pagination_response(items, total, page, actual_limit)

    async def get_chit_performance_report(self, tenant_id: UUID, page: int, limit: int, export: bool = False) -> ReportResponse:
        actual_limit = 0 if export else limit
        skip = 0 if export else (page - 1) * limit
        rows, total = await self.repo.get_chit_performance_report(tenant_id, skip, actual_limit)
        items = [ChitPerformanceReportItem(**r) for r in rows]
        return self._build_pagination_response(items, total, page, actual_limit)
