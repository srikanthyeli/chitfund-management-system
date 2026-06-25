from pydantic import BaseModel, Field, constr
from typing import List, Optional
from datetime import date, datetime
from uuid import UUID
from decimal import Decimal

# Shared enums and types can be handled via Literal or Enum, but strings are fine here
class PaymentCollectionRequest(BaseModel):
    payment_amount: Decimal = Field(..., gt=0, description="Amount paid, must be greater than zero")
    payment_date: date
    payment_method: constr(max_length=20) = "CASH"
    transaction_reference: Optional[constr(max_length=100)] = None
    remarks: Optional[str] = None
    client_request_id: constr(max_length=100) = Field(..., description="Idempotency key from client")

class MemberInfo(BaseModel):
    name: str
    phone: str

class ChitGroupInfo(BaseModel):
    name: str
    month_number: int
    share_count: int

class CollectorInfo(BaseModel):
    name: str

class PaymentReceiptResponse(BaseModel):
    id: UUID
    receipt_number: str
    payment_amount: Decimal
    payment_method: str
    payment_date: datetime
    status: str
    transaction_reference: Optional[str] = None
    remarks: Optional[str] = None
    reversal_reason: Optional[str] = None

class ReceiptDetailsResponse(BaseModel):
    receipt_number: str
    status: str
    payment_date: datetime
    payment_amount: Decimal
    payment_method: str
    member: MemberInfo
    chit_group: ChitGroupInfo
    due: dict  # Simplified due details
    collector: Optional[CollectorInfo] = None

class MemberDueResponse(BaseModel):
    id: UUID
    membership_id: UUID
    member_name: str
    member_phone: Optional[str] = None
    member_code: Optional[str] = None
    share_count: int
    gross_installment_amount: Decimal
    bonus_per_share: Decimal
    net_payable_amount: Decimal
    total_paid_amount: Decimal
    remaining_amount: Decimal
    payment_status: str
    due_date: Optional[date] = None
    last_payment_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CollectionSummaryData(BaseModel):
    total_memberships: int
    total_net_payable: Decimal
    total_collected: Decimal
    total_remaining: Decimal
    paid_count: int
    partial_count: int
    pending_count: int
    overdue_count: int

class CollectionSummaryResponse(BaseModel):
    summary: CollectionSummaryData
    dues: List[MemberDueResponse]

    class Config:
        from_attributes = True

class PaymentReversalRequest(BaseModel):
    reversal_reason: constr(min_length=5, max_length=500)

class PassbookDueEntry(BaseModel):
    chit_name: str
    month_number: int
    auction_date: date
    share_count: int
    gross_installment: Decimal
    bonus_per_share: Decimal
    total_bonus: Decimal
    net_payable: Decimal
    total_paid: Decimal
    remaining: Decimal
    payment_status: str
    receipt_numbers: List[str]

class MemberPassbookResponse(BaseModel):
    member_id: UUID
    member_name: str
    entries: List[PassbookDueEntry]
