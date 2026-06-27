from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Any, Dict
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal

class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total_records: int
    total_pages: int

class ReportResponse(BaseModel):
    data: List[Any]
    summary: Dict[str, Any]
    pagination: PaginationMeta

class DashboardMetricsResponse(BaseModel):
    total_chit_groups: int
    active_chit_groups: int
    completed_chit_groups: int
    total_members: int
    active_members: int
    replacement_members: int
    total_shares: int
    allocated_shares: int
    available_shares: int
    total_collections: Decimal
    todays_collections: Decimal
    current_month_collections: Decimal
    pending_collections: Decimal
    overdue_collections: Decimal
    collection_percentage: float
    total_auction_amount: Decimal
    total_winner_payouts: Decimal
    total_dividends: Decimal
    total_maintenance_charges: Decimal
    organizer_earnings: Decimal
    total_outstanding: Decimal
    net_cash_flow: Decimal
    # Chart Data
    monthly_collection_trend: List[Dict[str, Any]]
    monthly_payout_trend: List[Dict[str, Any]]
    payment_mode_distribution: List[Dict[str, Any]]
    collection_success_percentage: List[Dict[str, Any]]
    monthly_revenue: List[Dict[str, Any]]

class CollectionReportItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    receipt_id: UUID
    receipt_number: str
    member_name: str
    member_id: UUID
    chit_group_name: str
    shares: int
    month_number: int
    amount: Decimal
    payment_mode: str
    status: str
    collected_by: Optional[str]
    payment_date: datetime
    transaction_reference: Optional[str]

class PendingCollectionReportItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    due_id: UUID
    member_name: str
    mobile: str
    shares: int
    chit_group_name: str
    month_number: int
    expected_amount: Decimal
    paid_amount: Decimal
    pending_amount: Decimal
    overdue_days: int
    grace_period_end: Optional[date]

class AuctionReportItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    auction_id: UUID
    auction_month: int
    chit_group_name: str
    winner_name: Optional[str]
    gross_amount: Decimal
    discount_amount: Optional[Decimal]
    dividend_per_share: Optional[Decimal]
    auction_date: date
    status: str
    payout_status: str

class WinnerPayoutReportItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    payout_id: UUID
    winner_name: str
    chit_group_name: str
    month_number: int
    gross_amount: Decimal
    deductions: Decimal
    net_amount: Decimal
    payment_status: str
    payment_mode: str
    transaction_reference: Optional[str]
    receipt_number: str
    confirmation_status: str
    payout_date: date

class MemberFinancialReportItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    member_id: UUID
    member_name: str
    mobile: str
    total_paid: Decimal
    pending_amount: Decimal
    late_payments_count: int
    total_dividend_earned: Decimal
    total_winner_amount: Decimal
    current_balance: Decimal

class OrganizerFinancialReportItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    month: str # e.g. "2026-06"
    collections_received: Decimal
    maintenance_income: Decimal
    commission_income: Decimal
    total_outstanding: Decimal
    net_cash_flow: Decimal

class ChitPerformanceReportItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    chit_group_id: UUID
    chit_group_name: str
    status: str
    completion_percentage: float
    total_members: int
    total_collections: Decimal
    total_pending: Decimal
    auction_count: int
    risk_score: str # Low, Medium, High
