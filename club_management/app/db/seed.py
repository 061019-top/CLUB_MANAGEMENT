import argparse
from datetime import datetime, timedelta, timezone
from app.db.database import SessionLocal
from app.models.user import User, UserRole
from app.models.club import Club, ClubMember, ClubRole
from app.models.activity import ClubActivity, ActivityStatus, ActivityPriority
from app.core.security import get_password_hash, check_password_length
from app.services.club import record_audit


def create_demo_user(db, email, full_name, role, password):
    user = db.query(User).filter(User.email == email).first()
    if user is not None:
        return user

    user = User(
        email=email,
        full_name=full_name,
        role=role,
        password_hash=get_password_hash(password),
    )
    db.add(user)
    db.flush()
    return user


def create_demo_club(db, name, owner):
    club = db.query(Club).filter(Club.name == name, Club.owner_id == owner.id).first()
    if club is not None:
        return None

    club = Club(
        name=name,
        description='Dữ liệu mẫu phục vụ test và demo',
        owner_id=owner.id,
    )
    db.add(club)
    db.flush()
    record_audit(db, club.id, owner.id, 'CLUB_CREATED', {'name': name, 'source': 'seed'})
    return club


def add_demo_members(db, club, owner, member):
    owner_membership = ClubMember(club_id=club.id, user_id=owner.id, role=ClubRole.OWNER)
    member_membership = ClubMember(club_id=club.id, user_id=member.id, role=ClubRole.MEMBER)
    db.add(owner_membership)
    db.add(member_membership)
    record_audit(db, club.id, owner.id, 'MEMBER_ADDED', {'user_id': member.id, 'source': 'seed'})


def create_demo_activity(db, club, member, number, status, priority):
    activity = ClubActivity(
        club_id=club.id,
        title=f'{club.name}: hoạt động {number}',
        description='Hoạt động mẫu',
        assignee_id=member.id,
        status=status,
        priority=priority,
        due_date=datetime.now(timezone.utc) + timedelta(days=number),
    )
    db.add(activity)


def create_demo_activities(db, club, member):
    create_demo_activity(db, club, member, 1, ActivityStatus.TODO, ActivityPriority.LOW)
    create_demo_activity(db, club, member, 2, ActivityStatus.IN_PROGRESS, ActivityPriority.MEDIUM)
    create_demo_activity(db, club, member, 3, ActivityStatus.DONE, ActivityPriority.HIGH)


def seed(db, password):
    check_password_length(password)

    create_demo_user(db, 'admin@example.com', 'Demo Admin', UserRole.ADMIN, password)
    owner = create_demo_user(db, 'owner@example.com', 'Demo Owner', UserRole.USER, password)
    member = create_demo_user(db, 'member@example.com', 'Demo Member', UserRole.USER, password)

    club_names = ['Demo Coding Club', 'Demo Volunteer Club']
    for name in club_names:
        club = create_demo_club(db, name, owner)
        if club is not None:
            add_demo_members(db, club, owner, member)
            create_demo_activities(db, club, member)

    db.flush()


def main():
    parser = argparse.ArgumentParser(description='Tạo dữ liệu mẫu cho câu lạc bộ')
    parser.add_argument('--password', required=True, help='Mật khẩu cho tài khoản mẫu mới')
    args = parser.parse_args()

    db = SessionLocal()
    try:
        seed(db, args.password)
        db.commit()
        print('Đã tạo dữ liệu mẫu. Tài khoản và câu lạc bộ đã có được giữ nguyên.')
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == '__main__':
    main()
