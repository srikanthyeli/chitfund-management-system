from typing import Dict, Any, Optional
from uuid import UUID
from datetime import date
from decimal import Decimal

from src.shared.core.repository.financial_summary_repository import FinancialSummaryRepository
from src.shared.common.utils.date_range_utils import get_date_range

class FinancialSummaryService:
    def __init__(self, repo: FinancialSummaryRepository):
        self.repo = repo

    async def get_dashboard_summary(
        self,
        tenant_id: UUID,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        chit_group_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        
        start_date, end_date = get_date_range(date_from, date_to)
        
        raw_overview = await self.repo.get_dashboard_overview(
            tenant_id=tenant_id,
            date_from=start_date,
            date_to=end_date,
            chit_group_id=chit_group_id
        )
        
        net_cash = (
            raw_overview['total_collected'] 
            + raw_overview['commission'] 
            + raw_overview['maintenance'] 
            - raw_overview['payouts_paid'] 
            - raw_overview['dividends']
        )
        
        overview_data = {
            'total_collection': raw_overview['total_collected'],
            'pending_collection': raw_overview['total_pending'],
            'overdue_amount': raw_overview['total_overdue'],
            'winner_payouts_paid': raw_overview['payouts_paid'],
            'pending_winner_payouts': raw_overview['payouts_pending'],
            'organizer_commission_earned': raw_overview['commission'],
            'maintenance_charges_collected': raw_overview['maintenance'],
            'dividends_distributed': raw_overview['dividends'],
            'net_cash_position': net_cash
        }
        
        return {
            'overview': overview_data,
            'collection_vs_payout': [], # mock
            'chit_group_health': [], # mock
            'recent_activities': [], # mock
            'upcoming_actions': [] # mock
        }
