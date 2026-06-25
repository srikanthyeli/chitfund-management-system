from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal


# ─── Requests ────────────────────────────────────────────────────────────────

class CreateAuctionRequest(BaseModel):
    auction_month_number: int = Field(..., ge=1)
    auction_date: date
    maintenance_charge: Decimal = Field(..., ge=0)
    notes: Optional[str] = Field(None, max_length=1000)


class SubmitBidRequest(BaseModel):
    membership_id: UUID
    bid_discount_amount: Decimal = Field(..., gt=0)
    remarks: Optional[str] = Field(None, max_length=500)


# ─── Responses ────────────────────────────────────────────────────────────────

class AuctionResponse(BaseModel):
    id: UUID
    organizer_id: UUID
    chit_group_id: UUID
    auction_month_number: int
    auction_date: date
    status: str
    gross_chit_amount: Decimal
    maintenance_charge: Decimal
    maximum_bid_discount: Decimal
    total_discount_amount: Optional[Decimal] = None
    winner_membership_id: Optional[UUID] = None
    winner_member_id: Optional[UUID] = None
    winner_payout_amount: Optional[Decimal] = None
    bonus_per_share: Optional[Decimal] = None
    notes: Optional[str] = None
    finalized_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BidResponse(BaseModel):
    id: UUID
    chit_auction_id: UUID
    membership_id: UUID
    member_id: UUID
    member_name: Optional[str] = None
    member_code: Optional[str] = None
    share_count: Optional[int] = None
    bid_discount_amount: Decimal
    remarks: Optional[str] = None
    bid_time: datetime
    status: str
    is_highest: bool = False

    class Config:
        from_attributes = True


class EligibleMemberItem(BaseModel):
    membership_id: UUID
    member_id: UUID
    member_code: str
    full_name: str
    mobile: str
    share_count: int
    has_won_auction: bool


class WinnerDetail(BaseModel):
    membership_id: UUID
    member_id: UUID
    member_name: str
    member_code: str
    winning_discount: Decimal
    winner_payout_amount: Decimal
    bonus_per_share: Decimal


class AuctionDetailResponse(BaseModel):
    id: UUID
    organizer_id: UUID
    chit_group_id: UUID
    chit_name: str
    chit_code: str
    monthly_installment_per_share: Decimal
    total_shares: int
    auction_month_number: int
    auction_date: date
    status: str
    gross_chit_amount: Decimal
    maintenance_charge: Decimal
    maximum_bid_discount: Decimal
    total_discount_amount: Optional[Decimal] = None
    notes: Optional[str] = None
    finalized_at: Optional[datetime] = None
    bids: List[BidResponse] = []
    eligible_members: List[EligibleMemberItem] = []
    winner: Optional[WinnerDetail] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AuctionListItemResponse(BaseModel):
    id: UUID
    auction_month_number: int
    auction_date: date
    status: str
    gross_chit_amount: Decimal
    maintenance_charge: Decimal
    maximum_bid_discount: Decimal
    bid_count: int = 0
    highest_bid: Optional[Decimal] = None
    winner_payout_amount: Optional[Decimal] = None
    finalized_at: Optional[datetime] = None
    created_at: datetime


class AuctionListResponse(BaseModel):
    items: List[AuctionListItemResponse]
    total: int


class MonthlyDueResponse(BaseModel):
    id: UUID
    membership_id: UUID
    member_id: UUID
    member_name: Optional[str] = None
    member_code: Optional[str] = None
    month_number: int
    share_count: int
    gross_installment_amount: Decimal
    bonus_per_share: Decimal
    total_bonus_amount: Decimal
    net_payable_amount: Decimal
    payment_status: str
    due_date: Optional[date] = None
    remarks: Optional[str] = None

    class Config:
        from_attributes = True


class FinalizeAuctionPreview(BaseModel):
    """Preview data shown to the organizer before they confirm finalization."""
    auction_id: UUID
    auction_month_number: int
    winner_member_name: str
    winner_member_code: str
    winning_discount_amount: Decimal
    gross_chit_amount: Decimal
    maintenance_charge: Decimal
    winner_payout_amount: Decimal
    bonus_per_share: Decimal
    total_active_shares: int
    total_members: int
