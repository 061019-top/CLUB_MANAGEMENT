from pydantic import BaseModel, EmailStr , Field
from datetime import datetime
from typing import Optional 
from app.models.user import UserRole

class UserBase(BaseModel):
    email: EmailStr
    full_name: str =  Field(min_length=1, max_length=255)

class UserCreate(UserBase):
    password: str 

class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
