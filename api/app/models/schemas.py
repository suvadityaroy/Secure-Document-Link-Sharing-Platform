"""Pydantic models for request/response validation."""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRegister(BaseModel):
    """User registration request model."""
    username: str = Field(..., min_length=3, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=255)
    
    @field_validator('password')
    @classmethod
    def password_strength(cls, v):
        """Validate password strength."""
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserLogin(BaseModel):
    """User login request model."""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: str

    @field_validator('password')
    @classmethod
    def password_not_empty(cls, v):
        if not v:
            raise ValueError('Password is required')
        return v

    @classmethod
    def model_validate(cls, data, **kwargs):  # type: ignore[override]
        validated = super().model_validate(data, **kwargs)
        if not validated.username and not validated.email:
            raise ValueError('Either username or email is required')
        return validated


class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """User response model (safe to return to client)."""
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class FileUploadResponse(BaseModel):
    """Response from file upload to Java service."""
    file_id: str
    file_name: str
    file_size: int
    file_hash: str
    message: str


class CreateShareRequest(BaseModel):
    """Request to create a share link."""
    file_id: str
    file_name: str
    file_size: int
    file_hash: str
    one_time_access: bool = False
    expires_in_hours: Optional[int] = None  # None = no expiry


class ShareResponse(BaseModel):
    """Share link response model."""
    share_id: int
    share_token: str
    file_name: str
    file_size: int
    is_active: bool
    download_count: int
    one_time_access: bool
    expires_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class DownloadFileRequest(BaseModel):
    """Request to download file via share token."""
    share_token: str


class AccessLogResponse(BaseModel):
    """Access log response model."""
    file_share_id: int
    access_timestamp: datetime
    success: bool
    
    class Config:
        from_attributes = True
