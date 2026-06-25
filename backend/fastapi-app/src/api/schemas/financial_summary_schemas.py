from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal

class FinancialSummaryOverview(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    total_collection: Decimal = Decimal('0.00')
    pending_collection: Decimal = Decimal('0.00')
    overdue_amount: Decimal = Decimal('0.00')
    winner_payouts_paid: Decimal = Decimal('0.00')
    pending_winner_payouts: Decimal = Decimal('0.00')
    organizer_commission_earned: Decimal = Decimal('0.00')
    maintenance_charges_collected: Decimal = Decimal('0.00')
    dividends_distributed: Decimal = Decimal('0.00')
    net_cash_position: Decimal = Decimal('0.00')

class CollectionVsPayoutDataPoint(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    month_label: str
    collection_amount: Decimal = Decimal('0.00')
    winner_payout_amount: Decimal = Decimal('0.00')
    pending_collection_amount: Decimal = Decimal('0.00')

class ChitGroupHealth(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    chit_group_id: UUID
    chit_group_name: str
    chit_code: str
    current_month: int
    total_expected_collection: Decimal = Decimal('0.00')
    total_collected: Decimal = Decimal('0.00')
    pending_amount: Decimal = Decimal('0.00')
    overdue_amount: Decimal = Decimal('0.00')
    total_winner_payout_amount: Decimal = Decimal('0.00')
    dividend_distributed: Decimal = Decimal('0.00')
    commission_earned: Decimal = Decimal('0.00')
    collection_percentage: float = 0.0
    financial_health_status: str  # Healthy, Attention Needed, Critical

class RecentActivity(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    activity_type: str
    description: str
    amount: Optional[Decimal] = None
    created_at: datetime
    chit_group_name: Optional[str] = None

class UpcomingAction(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    action_type: str
    description: str
    due_date: Optional[date] = None
    amount: Optional[Decimal] = None
    chit_group_id: Optional[UUID] = None
    member_id: Optional[UUID] = None
    
class FinancialSummaryResponse(BaseModel):
    overview: FinancialSummaryOverview
    collection_vs_payout: List[CollectionVsPayoutDataPoint]
    chit_group_health: List[ChitGroupHealth]
    recent_activities: List[RecentActivity]
    upcoming_actions: List[UpcomingAction]
