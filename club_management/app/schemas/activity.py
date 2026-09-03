from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime, timezone
from typing import Optional
from app.models.activity import ActivityStatus, ActivityPriority


class ActivityBase(BaseModel):
    model_config = ConfigDict(extra='forbid')
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    assignee_id: Optional[int] = Field(default=None, gt=0, le=2147483647)
    status: ActivityStatus = ActivityStatus.TODO
    priority: ActivityPriority = ActivityPriority.MEDIUM
    due_date: Optional[datetime] = None

    @field_validator('title')
    @classmethod
    def validate_title(cls, value):
        if value is None or not value.strip():
            raise ValueError('Tiêu đề không được để trống')
        return value.strip()

    @field_validator('description')
    @classmethod
    def validate_description(cls, value):
        if value is not None and len(value.encode('utf-8')) > 65535:
            raise ValueError('Mô tả vượt giới hạn TEXT 65535 byte')
        return value

    @field_validator('due_date')
    @classmethod
    def normalize_due_date(cls, value):
        if value is not None:
            if value.tzinfo is not None:
                value = value.astimezone(timezone.utc).replace(tzinfo=None)
            if value.year < 1000:
                raise ValueError('Ngày phải từ năm 1000 theo DATETIME MySQL')
        return value


class ActivityCreate(ActivityBase):
    pass


class ActivityUpdate(ActivityBase):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    status: Optional[ActivityStatus] = None
    priority: Optional[ActivityPriority] = None

    @field_validator('title', 'status', 'priority')
    @classmethod
    def reject_null(cls, value):
        if value is None:
            raise ValueError('Trường này không được là null')
        return value


class ActivityResponse(ActivityBase):
    id: int
    club_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
