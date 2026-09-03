from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime,timezone
from app.db.database import Base
import enum

class ActivityStatus(str, enum.Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"

class ActivityPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class ClubActivity(Base):
    __tablename__ = "club_activities"

    id = Column(Integer, primary_key=True, index=True)
    club_id = Column(Integer, ForeignKey("clubs.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(Enum(ActivityStatus), default=ActivityStatus.TODO, nullable=False)
    priority = Column(Enum(ActivityPriority), default=ActivityPriority.MEDIUM, nullable=False)
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    club = relationship("Club", back_populates="activities")
    assignee = relationship("User", back_populates="activities")
