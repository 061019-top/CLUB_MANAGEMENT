from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.activity import ActivityStatus, ActivityPriority

class ActivityBase(BaseModel):
    title: str
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    status: ActivityStatus = ActivityStatus.TODO
    priority: ActivityPriority = ActivityPriority.MEDIUM
    due_date: Optional[datetime] = None

class ActivityCreate(ActivityBase):
    pass

class ActivityUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    status: Optional[ActivityStatus] = None
    priority: Optional[ActivityPriority] = None
    due_date: Optional[datetime] = None

class ActivityResponse(ActivityBase):
    id: int
    club_id: int
    created_at: datetime

    class Config:
        from_attributes = True
