"""
User Schemas
Pydantic models for user-related API requests and responses.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import uuid


class UserRegister(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str
    full_name: str


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class UserProfileUpdate(BaseModel):
    """Schema for updating user profile."""
    full_name: Optional[str] = None
    bio: Optional[str] = None
    profile_data: Optional[dict] = None


class UserResponse(BaseModel):
    """Schema for user response (no sensitive data)."""
    id: uuid.UUID
    email: str
    full_name: str
    bio: Optional[str] = None
    profile_data: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
