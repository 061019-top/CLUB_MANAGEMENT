from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from app.models.club import Club, ClubMember, ClubRole, AuditLog
from app.models.user import User

def get_club_or_404(club_id: int, db: Session) -> Club:

    club = db.query(Club).filter(Club.id == club_id, Club.deleted_at.is_(None)).first()
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Câu lạc bộ với id={club_id} không tồn tại",
        )
    return club


def get_membership(club_id: int, user_id: int, db: Session) -> Optional[ClubMember]:

    return (
        db.query(ClubMember)
        .filter(ClubMember.club_id == club_id, ClubMember.user_id == user_id)
        .first()
    )


def require_membership(club_id: int, user: User, db: Session) -> ClubMember:

    get_club_or_404(club_id, db)
    membership = get_membership(club_id, user.id, db)
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không phải thành viên của câu lạc bộ này",
        )
    return membership


def require_owner(club_id: int, user: User, db: Session) -> ClubMember:

    membership = require_membership(club_id, user, db)
    if membership.role != ClubRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ OWNER mới có quyền thực hiện thao tác này",
        )
    return membership


def record_audit(db: Session, club_id: int, actor_id: int, action: str, details: dict):
    db.add(AuditLog(club_id=club_id, actor_id=actor_id, action=action, details=details))
