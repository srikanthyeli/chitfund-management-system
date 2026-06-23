from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional

class LoginRequest(BaseModel):
    mobile: str = Field(..., description="User mobile number")
    password: str = Field(..., min_length=6, description="User password")

class UserResponse(BaseModel):
    id: UUID
    mobile: str
    role: str

    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int
    user: UserResponse

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class TokenPayload(BaseModel):
    sub: str
    role: str
    type: str
    exp: int

class CurrentUserResponse(BaseModel):
    id: UUID
    mobile: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True
