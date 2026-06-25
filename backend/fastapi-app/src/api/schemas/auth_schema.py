from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional

class LoginRequest(BaseModel):
    mobile: str = Field(..., description="User mobile number")
    password: str = Field(..., description="User password")
    device_id: Optional[str] = None
    device_name: Optional[str] = None

class ForceLoginRequest(BaseModel):
    mobile: str = Field(..., description="User mobile number")
    password: str = Field(..., description="User password")
    device_id: Optional[str] = None
    device_name: Optional[str] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class CurrentUserResponse(BaseModel):
    id: UUID
    mobile: str
    role: str
    organizer_id: Optional[UUID] = None
    name: str
    must_change_password: bool

    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: CurrentUserResponse

class LogoutResponse(BaseModel):
    success: bool
    message: str
