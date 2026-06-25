from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, date

class MemberDashboardStats(BaseModel):
    active_chit_groups: int
    total_shares_held: int
    current_month_due: float
    pending_overdue_amount: float
    payments_made_this_month: float
    total_dividends_earned: float

class UpcomingDueResponse(BaseModel):
    chit_group_id: UUID
    chit_group_name: str
    month_number: int
    due_date: Optional[date]
    amount_due: float
    status: str

class RecentPaymentResponse(BaseModel):
    receipt_id: UUID
    receipt_number: str
    chit_group_name: str
    amount: float
    payment_date: datetime
    status: str

class RecentAuctionResponse(BaseModel):
    auction_id: UUID
    chit_group_name: str
    month_number: int
    winner_name: Optional[str]
    winning_discount: float
    dividend_per_share: float
    auction_date: date

class WinnerPayoutPreviewResponse(BaseModel):
    payout_id: UUID
    status: str
    net_payout_amount: float

class MemberDashboardResponse(BaseModel):
    stats: MemberDashboardStats
    upcoming_dues: List[UpcomingDueResponse]
    recent_payments: List[RecentPaymentResponse]
    recent_auctions: List[RecentAuctionResponse]
    winner_payouts: List[WinnerPayoutPreviewResponse]

class ChitSummaryResponse(BaseModel):
    chit_group_id: UUID
    chit_group_name: str
    chit_code: str
    organizer_name: str
    start_date: date
    duration_months: int
    current_month: int
    status: str
    shares_held: int
    monthly_installment_per_share: float
    total_monthly_payable: float
    next_due_date: Optional[date]
    current_payment_status: str

class NotificationResponse(BaseModel):
    id: UUID
    notification_type: str
    title: str
    message: str
    reference_type: Optional[str]
    reference_id: Optional[str]
    is_read: bool
    created_at: datetime

class NotificationListResponse(BaseModel):
    items: List[NotificationResponse]
    total: int
    page: int
    page_size: int

class ProfileUpdateResponse(BaseModel):
    status: bool
    message: str
