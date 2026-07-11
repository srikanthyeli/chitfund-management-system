from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional

class MemberOTPRequest(BaseModel):
    mobile: str = Field(..., description="Member mobile number")

class MemberSetPasswordRequest(BaseModel):
    mobile: str = Field(..., description="Member mobile number")
    otp: str = Field(..., description="OTP sent to mobile")
    new_password: str = Field(..., description="New password to set")

class MemberLoginRequest(BaseModel):
    mobile: str = Field(..., description="Member mobile number")
    password: str = Field(..., description="Member password")
    device_id: Optional[str] = None
    device_name: Optional[str] = None

class CurrentMemberResponse(BaseModel):
    id: UUID
    mobile: str
    role: str = "MEMBER"
    organizer_id: UUID
    name: str
    member_code: str

    class Config:
        from_attributes = True

class MemberLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: CurrentMemberResponse
