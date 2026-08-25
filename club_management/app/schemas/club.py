from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional
from app.models.club import ClubRole
from app.schemas.user import UserResponse


class ClubBase(BaseModel):
    name: str
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Tên câu lạc bộ không được để trống")
        if len(v.strip()) > 255:
            raise ValueError("Tên câu lạc bộ không được vượt quá 255 ký tự")
        return v.strip()


class ClubCreate(ClubBase):
    pass


class ClubUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v.strip():
                raise ValueError("Tên câu lạc bộ không được để trống")
            if len(v.strip()) > 255:
                raise ValueError("Tên câu lạc bộ không được vượt quá 255 ký tự")
            return v.strip()
        return v


class ClubResponse(ClubBase):
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ClubMemberResponse(BaseModel):
    club_id: int
    user_id: int
    role: ClubRole
    joined_at: datetime

    class Config:
        from_attributes = True


class ClubMemberDetailResponse(BaseModel):
    club_id: int
    user_id: int
    role: ClubRole
    joined_at: datetime
    user: Optional[UserResponse] = None

    class Config:
        from_attributes = True


class AddMemberRequest(BaseModel):
    user_id: int
