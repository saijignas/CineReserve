"""User Pydantic schemas."""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)

class UserCreate(UserBase):
    """Schema for user creation."""
    password: str = Field(..., min_length=8, max_length=100)

class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    """Schema for user update."""
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None

class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    """Schema for token payload."""
    sub: int
    type: str
    exp: datetime

class LogoutRequest(BaseModel):
    """Schema for logout request."""
    refresh_token: Optional[str] = None
