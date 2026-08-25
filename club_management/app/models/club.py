from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime,timezone
from app.db.database import Base
import enum

class ClubRole(str, enum.Enum):
    OWNER = "OWNER"
    MEMBER = "MEMBER"

class Club(Base):
    __tablename__ = "clubs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime,default=lambda: datetime.now(timezone.utc), nullable=False)

    owner = relationship("User", back_populates="clubs")
    members = relationship("ClubMember", back_populates="club", cascade="all, delete-orphan")
    activities = relationship("ClubActivity", back_populates="club", cascade="all, delete-orphan")

class ClubMember(Base):
    __tablename__ = "club_members"

    club_id = Column(Integer, ForeignKey("clubs.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    role = Column(Enum(ClubRole), nullable=False)
    joined_at = Column(DateTime,default=lambda: datetime.now(timezone.utc), nullable=False)

    club = relationship("Club", back_populates="members")
    user = relationship("User", back_populates="club_memberships")
