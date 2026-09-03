from pydantic import BaseModel, field_validator, Field, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.club import ClubRole
from app.schemas.user import UserResponse


class ClubBase(BaseModel):
    model_config = ConfigDict(extra="forbid")
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



    @field_validator('description')
    @classmethod
    def validate_description(cls, value):
        if value is not None and len(value.encode('utf-8')) > 65535:
            raise ValueError('Mô tả vượt giới hạn TEXT 65535 byte')
        return value


class ClubCreate(ClubBase):
    pass


class ClubUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Optional[str] = None
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            raise ValueError('Tên câu lạc bộ không được là null')
        if v is not None:
            if not v.strip():
                raise ValueError("Tên câu lạc bộ không được để trống")
            if len(v.strip()) > 255:
                raise ValueError("Tên câu lạc bộ không được vượt quá 255 ký tự")
            return v.strip()
        return v



    @field_validator('description')
    @classmethod
    def validate_description(cls, value):
        if value is not None and len(value.encode('utf-8')) > 65535:
            raise ValueError('Mô tả vượt giới hạn TEXT 65535 byte')
        return value


class ClubResponse(ClubBase):
    id: int
    owner_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ClubMemberResponse(BaseModel):
    club_id: int
    user_id: int
    role: ClubRole
    joined_at: datetime

    model_config = {"from_attributes": True}


class ClubMemberDetailResponse(BaseModel):
    club_id: int
    user_id: int
    role: ClubRole
    joined_at: datetime
    user: Optional[UserResponse] = None

    model_config = {"from_attributes": True}


class AddMemberRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    user_id: int = Field(gt=0, le=2147483647)
