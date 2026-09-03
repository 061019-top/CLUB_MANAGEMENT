from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.user import UserRole
from app.core.security import check_password_length

class UserBase(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr = Field(max_length=255)
    full_name: str =  Field(min_length=1, max_length=255)

    @field_validator('full_name')
    @classmethod
    def clean_name(cls, value):
        if not value.strip():
            raise ValueError('Họ tên không được để trống')
        return value.strip()

    @field_validator('email')
    @classmethod
    def normalize_email(cls, value):
        return value.lower()

class UserCreate(UserBase):
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, value):
        return check_password_length(value)


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=255)

    @field_validator('full_name')
    @classmethod
    def clean_name(cls, value):
        if value is None or not value.strip():
            raise ValueError('Họ tên không được để trống')
        return value.strip()

class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
