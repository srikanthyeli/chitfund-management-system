from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

class MemberCreateRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=150)
    mobile: str = Field(..., max_length=15)
    alternate_mobile: Optional[str] = Field(None, max_length=15)
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    village: Optional[str] = Field(None, max_length=100)
    mandal: Optional[str] = Field(None, max_length=100)
    district: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    pincode: Optional[str] = Field(None, max_length=10)
    aadhaar_last4: Optional[str] = Field(None, max_length=4)
    notes: Optional[str] = None

class MemberUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=150)
    alternate_mobile: Optional[str] = Field(None, max_length=15)
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    village: Optional[str] = Field(None, max_length=100)
    mandal: Optional[str] = Field(None, max_length=100)
    district: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    pincode: Optional[str] = Field(None, max_length=10)
    aadhaar_last4: Optional[str] = Field(None, max_length=4)
    notes: Optional[str] = None

class MemberStatusRequest(BaseModel):
    is_active: bool
    remarks: Optional[str] = Field(None, max_length=500)

class MemberMobileUpdateRequest(BaseModel):
    old_mobile: str = Field(..., max_length=15)
    new_mobile: str = Field(..., max_length=15)
    confirm_new_mobile: str = Field(..., max_length=15)

class MemberResponse(BaseModel):
    id: UUID
    organizer_id: UUID
    member_code: str
    full_name: str
    mobile: str
    alternate_mobile: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    village: Optional[str] = None
    mandal: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    aadhaar_last4: Optional[str] = None
    notes: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class MemberListItemResponse(BaseModel):
    id: UUID
    member_code: str
    full_name: str
    mobile: str
    village: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class MemberListResponse(BaseModel):
    items: List[MemberListItemResponse]
    page: int
    page_size: int
    total: int
    total_pages: int

class MemberActivityResponse(BaseModel):
    id: UUID
    action_type: str
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    remarks: Optional[str] = None
    performed_by: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True

class MemberSummaryResponse(BaseModel):
    total_members: int
    active_members: int
    inactive_members: int
    new_members_this_month: int
