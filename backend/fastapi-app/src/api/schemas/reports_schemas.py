from pydantic import BaseModel, ConfigDict
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

class ChitGroupReportItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    chit_group_id: UUID
    chit_group_name: str
    code: str
    status: str
    total_chit_value: Decimal
    total_shares: int
    current_month: int
    expected_collection: Decimal
    collected_amount: Decimal
    pending_amount: Decimal
    overdue_amount: Decimal
    total_payouts: Decimal
    total_dividends: Decimal
    total_commission: Decimal
    collection_percentage: float
    financial_health_status: str

class CollectionReportItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    receipt_id: UUID
    payment_date: datetime
    receipt_number: str
    chit_group_name: str
    month_number: int
    member_name: str
    number_of_shares: int
    expected_amount: Decimal
    paid_amount: Decimal
    pending_amount: Decimal
    payment_mode: str
    transaction_reference: Optional[str]
    status: str

class PayoutReportItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    payout_id: UUID
    payout_receipt_number: str
    chit_group_name: str
    month_number: int
    winner_member_name: str
    gross_chit_value: Decimal
    winning_discount: Decimal
    commission: Decimal
    maintenance_charge: Decimal
    net_payout: Decimal
    payment_mode: str
    transaction_reference: Optional[str]
    paid_date: Optional[date]
    status: str

class OverdueReportItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    due_id: UUID
    member_name: str
    mobile_number: str
    chit_group_name: str
    shares_held: int
    month_number: int
    due_date: Optional[date]
    expected_amount: Decimal
    paid_amount: Decimal
    pending_amount: Decimal
    overdue_days: int
    last_payment_date: Optional[datetime]

class CommissionReportItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    auction_id: UUID
    chit_group_name: str
    month_number: int
    auction_date: date
    gross_chit_value: Decimal
    winning_discount: Decimal
    organizer_commission: Decimal
    maintenance_charge: Decimal
    status: str

class DividendReportItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    closure_id: UUID
    chit_group_name: str
    month_number: int
    dividend_pool: Decimal
    dividend_per_share: Decimal
    total_eligible_shares: int
    total_dividend_distributed: Decimal
    status: str

class ReceiptReportItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    receipt_id: UUID
    receipt_number: str
    receipt_type: str # 'COLLECTION' or 'PAYOUT'
    entity_name: str # Member name
    chit_group_name: str
    month_number: int
    amount: Decimal
    created_date: datetime
    status: str
