from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from uuid import UUID

class WinnerPayoutCreateRequest(BaseModel):
    auction_id: UUID
    due_date: Optional[date] = None
    payment_notes: Optional[str] = None

class WinnerPayoutUpdateRequest(BaseModel):
    due_date: Optional[date] = None
    payment_notes: Optional[str] = None

class WinnerPayoutInitiatePaymentRequest(BaseModel):
    payment_notes: Optional[str] = None

class WinnerPayoutMarkPaidRequest(BaseModel):
    payment_mode: str
    transaction_reference: Optional[str] = None
    bank_name: Optional[str] = None
    paid_at: datetime
    payment_notes: Optional[str] = None
    proof_file_url: Optional[str] = None

class WinnerPayoutConfirmReceivedRequest(BaseModel):
    confirmation_note: Optional[str] = None

class WinnerPayoutCancelRequest(BaseModel):
    reason: str

class WinnerPayoutReverseRequest(BaseModel):
    reason: str
    reversal_reference: Optional[str] = None

class WinnerPayoutShareResponse(BaseModel):
    receipt_number: str
    receipt_url: str
    receipt_image_url: Optional[str] = None
    whatsapp_message: str
    whatsapp_share_url: str
