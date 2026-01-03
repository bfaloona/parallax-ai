"""Authentication schemas for request/response validation."""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID


class UserRegister(BaseModel):
    """Schema for user registration request."""

    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")


class UserLogin(BaseModel):
    """Schema for user login request."""

    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for decoded JWT token data."""

    user_id: UUID | None = None


class UserResponse(BaseModel):
    """Schema for user data in API responses."""

    id: UUID
    email: str
    tier: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True  # Allows creating from ORM models
