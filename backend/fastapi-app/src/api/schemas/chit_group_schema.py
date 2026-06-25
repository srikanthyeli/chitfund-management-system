from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal

class ChitGroupCreateRequest(BaseModel):
    chit_name: str = Field(..., min_length=2, max_length=150)
    description: Optional[str] = None
    total_chit_value: Decimal = Field(..., gt=0)
    monthly_installment_per_share: Decimal = Field(..., gt=0)
    total_shares: int = Field(..., ge=2)
    duration_months: int = Field(..., ge=2)
    maintenance_charge: Decimal = Field(default=Decimal('0'), ge=0)
    maintenance_charge_type: str = Field(default="FIXED")
    start_date: date
    installment_due_day: int = Field(default=1, ge=1, le=28)

    @field_validator('start_date')
    @classmethod
    def validate_start_date(cls, v: date) -> date:
        if v.day != 1:
            raise ValueError("Chit start date must be the first day of a month")
        return v

    @field_validator('maintenance_charge_type')
    @classmethod
    def validate_charge_type(cls, v: str) -> str:
        if v not in ('FIXED', 'PERCENTAGE'):
            raise ValueError("maintenance_charge_type must be FIXED or PERCENTAGE")
        return v

    @model_validator(mode='after')
    def validate_financials(self) -> 'ChitGroupCreateRequest':
        if self.duration_months != self.total_shares:
            raise ValueError("duration_months must equal total_shares")
        
        expected_value = self.monthly_installment_per_share * self.total_shares
        if self.total_chit_value != expected_value:
            raise ValueError(f"total_chit_value ({self.total_chit_value}) must equal monthly_installment_per_share * total_shares ({expected_value})")
        
        if self.maintenance_charge_type == 'PERCENTAGE':
            if self.maintenance_charge < 0 or self.maintenance_charge > 100:
                raise ValueError("Percentage maintenance charge must be between 0 and 100")
        return self


class ChitGroupUpdateRequest(BaseModel):
    chit_name: Optional[str] = Field(None, min_length=2, max_length=150)
    description: Optional[str] = None
    total_chit_value: Optional[Decimal] = Field(None, gt=0)
    monthly_installment_per_share: Optional[Decimal] = Field(None, gt=0)
    total_shares: Optional[int] = Field(None, ge=2)
    duration_months: Optional[int] = Field(None, ge=2)
    maintenance_charge: Optional[Decimal] = Field(None, ge=0)
    maintenance_charge_type: Optional[str] = None
    start_date: Optional[date] = None
    installment_due_day: Optional[int] = Field(None, ge=1, le=28)

    @field_validator('start_date')
    @classmethod
    def validate_start_date(cls, v: Optional[date]) -> Optional[date]:
        if v is not None and v.day != 1:
            raise ValueError("Chit start date must be the first day of a month")
        return v

    @field_validator('maintenance_charge_type')
    @classmethod
    def validate_charge_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ('FIXED', 'PERCENTAGE'):
            raise ValueError("maintenance_charge_type must be FIXED or PERCENTAGE")
        return v

    @model_validator(mode='after')
    def validate_financials(self) -> 'ChitGroupUpdateRequest':
        t_shares = self.total_shares
        d_months = self.duration_months
        t_val = self.total_chit_value
        m_inst = self.monthly_installment_per_share
        m_type = self.maintenance_charge_type
        m_charge = self.maintenance_charge

        if t_shares is not None and d_months is not None and t_shares != d_months:
            raise ValueError("duration_months must equal total_shares")

        if t_val is not None and m_inst is not None and t_shares is not None:
            expected = m_inst * t_shares
            if t_val != expected:
                raise ValueError("total_chit_value must equal monthly_installment_per_share * total_shares")

        if m_type == 'PERCENTAGE' and m_charge is not None:
            if m_charge < 0 or m_charge > 100:
                raise ValueError("Percentage maintenance charge must be between 0 and 100")
        return self


class ChitMembershipCreateRequest(BaseModel):
    member_id: UUID
    share_count: int = Field(..., ge=1)
    remarks: Optional[str] = Field(None, max_length=500)


class ChitMembershipUpdateRequest(BaseModel):
    share_count: int = Field(..., ge=1)
    remarks: Optional[str] = Field(None, max_length=500)


class BulkMembershipAllocateRequest(BaseModel):
    member_ids: List[UUID]
    share_count_per_member: int = Field(..., gt=0)
    remarks: Optional[str] = Field(None, max_length=500)



class ChitStatusChangeRequest(BaseModel):
    status: str
    remarks: Optional[str] = Field(None, max_length=500)


class ChitGroupResponse(BaseModel):
    id: UUID
    organizer_id: UUID
    chit_code: str
    chit_name: str
    description: Optional[str] = None
    total_chit_value: Decimal
    monthly_installment_per_share: Decimal
    total_shares: int
    duration_months: int
    maintenance_charge: Decimal
    maintenance_charge_type: str
    start_date: date
    installment_due_day: int
    status: str
    allocated_shares: int
    available_shares: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChitGroupListItemResponse(BaseModel):
    id: UUID
    chit_code: str
    chit_name: str
    total_chit_value: Decimal
    monthly_installment_per_share: Decimal
    total_shares: int
    allocated_shares: int
    available_shares: int
    start_date: date
    status: str

    class Config:
        from_attributes = True


class ChitMembershipResponse(BaseModel):
    id: UUID
    organizer_id: UUID
    chit_group_id: UUID
    member_id: UUID
    share_count: int
    joined_at: datetime
    status: str
    remarks: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BulkMembershipAllocateResponse(BaseModel):
    message: str
    chit_group_id: UUID
    selected_member_count: int
    share_count_per_member: int
    shares_added: int
    total_allocated_shares: int
    available_shares: int
    created_membership_count: int
    updated_membership_count: int
    memberships: List[ChitMembershipResponse]


class ChitMembershipDetailItem(BaseModel):
    membership_id: UUID
    member_id: UUID
    member_code: str
    full_name: str
    mobile: str
    village: Optional[str] = None
    share_count: int
    membership_status: str


class ChitGroupDetailResponse(BaseModel):
    id: UUID
    organizer_id: UUID
    chit_code: str
    chit_name: str
    description: Optional[str] = None
    total_chit_value: Decimal
    monthly_installment_per_share: Decimal
    total_shares: int
    duration_months: int
    maintenance_charge: Decimal
    maintenance_charge_type: str
    start_date: date
    installment_due_day: int
    status: str
    allocated_shares: int
    available_shares: int
    member_count: int
    monthly_pool: Decimal
    memberships: List[ChitMembershipDetailItem]
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChitGroupActivityResponse(BaseModel):
    id: UUID
    organizer_id: UUID
    chit_group_id: UUID
    membership_id: Optional[UUID] = None
    action_type: str
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    remarks: Optional[str] = None
    performed_by_user_id: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChitGroupSummaryResponse(BaseModel):
    total_chits: int
    draft_chits: int
    ready_to_start_chits: int
    active_chits: int
    total_allocated_shares: int
    total_available_shares: int
    upcoming_chits_count: int


class ChitGroupListResponse(BaseModel):
    items: List[ChitGroupListItemResponse]
    page: int
    page_size: int
    total: int
    total_pages: int

