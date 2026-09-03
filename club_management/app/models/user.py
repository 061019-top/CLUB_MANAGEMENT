from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime,timezone
from app.db.database import Base
import enum

class UserRole(str, enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    clubs = relationship("Club", back_populates="owner")
    club_memberships = relationship("ClubMember", back_populates="user")
    activities = relationship("ClubActivity", back_populates="assignee")
