from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class OrganizerCreateRequest(BaseModel):
    name: str = Field(..., max_length=150)
    mobile: str = Field(..., max_length=15)
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    village: Optional[str] = None
    mandal: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = Field(None, max_length=10)

class OrganizerCreateResponse(BaseModel):
    id: UUID
    organizer_code: str
    name: str
    mobile: str
    login_mobile: str
    temporary_password: str

class OrganizerUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, max_length=150)
    mobile: Optional[str] = Field(None, max_length=15)
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    village: Optional[str] = None
    mandal: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = Field(None, max_length=10)

class OrganizerStatusRequest(BaseModel):
    is_active: bool

class OrganizerResponse(BaseModel):
    id: UUID
    organizer_code: str
    name: str
    mobile: str
    email: Optional[str] = None
    address: Optional[str] = None
    village: Optional[str] = None
    mandal: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class OrganizerListResponse(BaseModel):
    items: List[OrganizerResponse]
    total: int
