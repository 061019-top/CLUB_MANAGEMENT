from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.club import Club, ClubMember, ClubRole
from app.schemas.club import (
    ClubCreate,
    ClubUpdate,
    ClubResponse,
    ClubMemberResponse,
    ClubMemberDetailResponse,
    AddMemberRequest,
)
from app.utils.response import build_response

router = APIRouter(prefix="/clubs", tags=["Câu lạc bộ"])


def get_club_or_404(club_id: int, db: Session) -> Club:
    """Lấy câu lạc bộ hoặc raise 404."""
    club = db.query(Club).filter(Club.id == club_id).first()
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Câu lạc bộ với id={club_id} không tồn tại",
        )
    return club


def get_membership(club_id: int, user_id: int, db: Session) -> Optional[ClubMember]:
    """Lấy bản ghi thành viên nếu tồn tại."""
    return (
        db.query(ClubMember)
        .filter(ClubMember.club_id == club_id, ClubMember.user_id == user_id)
        .first()
    )


def require_membership(club_id: int, user: User, db: Session) -> ClubMember:
    """Yêu cầu user phải là thành viên câu lạc bộ."""
    membership = get_membership(club_id, user.id, db)
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không phải thành viên của câu lạc bộ này",
        )
    return membership


def require_owner(club_id: int, user: User, db: Session) -> ClubMember:
    """Yêu cầu user phải là OWNER của câu lạc bộ."""
    membership = require_membership(club_id, user, db)
    if membership.role != ClubRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ OWNER mới có quyền thực hiện thao tác này",
        )
    return membership


# ───────────────────────── CLUBS ─────────────────────────

@router.post("", status_code=status.HTTP_201_CREATED, summary="Tạo câu lạc bộ mới")
def create_club(
    request: Request,
    club_in: ClubCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Tạo câu lạc bộ mới. Người tạo tự động trở thành **OWNER**.
    """
    new_club = Club(
        name=club_in.name,
        description=club_in.description,
        owner_id=current_user.id,
    )
    db.add(new_club)
    db.flush()  # để lấy new_club.id trước khi commit

    # Tự động thêm người tạo vào bảng club_members với role OWNER
    owner_membership = ClubMember(
        club_id=new_club.id,
        user_id=current_user.id,
        role=ClubRole.OWNER,
    )
    db.add(owner_membership)
    db.commit()
    db.refresh(new_club)

    return build_response(
        status_code=201,
        message="Tạo câu lạc bộ thành công",
        path=request.url.path,
        data=ClubResponse.model_validate(new_club).model_dump(),
    )


@router.get("", summary="Danh sách câu lạc bộ của tôi")
def list_clubs(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    search: Optional[str] = Query(None, description="Tìm theo tên câu lạc bộ"),
):
    """
    Trả về danh sách câu lạc bộ mà user hiện tại là **owner** hoặc **member**.
    Hỗ trợ tìm kiếm theo tên.
    """
    query = (
        db.query(Club)
        .join(ClubMember, ClubMember.club_id == Club.id)
        .filter(ClubMember.user_id == current_user.id)
    )

    if search:
        query = query.filter(Club.name.ilike(f"%{search}%"))

    clubs = query.all()
    data = [ClubResponse.model_validate(c).model_dump() for c in clubs]

    return build_response(
        status_code=200,
        message="Thành công",
        path=request.url.path,
        data=data,
    )


@router.get("/{club_id}", summary="Chi tiết câu lạc bộ")
def get_club(
    request: Request,
    club_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Trả về thông tin chi tiết câu lạc bộ. Chỉ **thành viên** câu lạc bộ mới được xem.
    """
    club = get_club_or_404(club_id, db)
    require_membership(club_id, current_user, db)

    return build_response(
        status_code=200,
        message="Thành công",
        path=request.url.path,
        data=ClubResponse.model_validate(club).model_dump(),
    )


@router.patch("/{club_id}", summary="Cập nhật câu lạc bộ")
def update_club(
    request: Request,
    club_id: int,
    club_in: ClubUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Cập nhật thông tin câu lạc bộ. Chỉ **OWNER** mới có quyền.
    Chỉ cập nhật những trường được gửi lên.
    """
    club = get_club_or_404(club_id, db)
    require_owner(club_id, current_user, db)

    update_data = club_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(club, field, value)

    db.commit()
    db.refresh(club)

    return build_response(
        status_code=200,
        message="Cập nhật câu lạc bộ thành công",
        path=request.url.path,
        data=ClubResponse.model_validate(club).model_dump(),
    )


@router.delete("/{club_id}", status_code=status.HTTP_200_OK, summary="Xóa câu lạc bộ")
def delete_club(
    request: Request,
    club_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Xóa câu lạc bộ (kèm toàn bộ thành viên và hoạt động). Chỉ **OWNER** mới có quyền.
    """
    club = get_club_or_404(club_id, db)
    require_owner(club_id, current_user, db)

    db.delete(club)
    db.commit()

    return build_response(
        status_code=200,
        message="Xóa câu lạc bộ thành công",
        path=request.url.path,
        data=None,
    )


# ───────────────────────── MEMBERS ─────────────────────────

@router.post("/{club_id}/members", status_code=status.HTTP_201_CREATED, summary="Thêm thành viên vào câu lạc bộ")
def add_member(
    request: Request,
    club_id: int,
    body: AddMemberRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Thêm một user vào câu lạc bộ với role **MEMBER**. Chỉ **OWNER** mới có quyền.
    Không cho phép thêm user đã là thành viên.
    """
    get_club_or_404(club_id, db)
    require_owner(club_id, current_user, db)

    # Kiểm tra user cần thêm có tồn tại không
    target_user = db.query(User).filter(User.id == body.user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Người dùng với id={body.user_id} không tồn tại",
        )

    # Kiểm tra đã là thành viên chưa
    existing = get_membership(club_id, body.user_id, db)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Người dùng đã là thành viên của câu lạc bộ này",
        )

    new_member = ClubMember(
        club_id=club_id,
        user_id=body.user_id,
        role=ClubRole.MEMBER,
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)

    return build_response(
        status_code=201,
        message="Thêm thành viên thành công",
        path=request.url.path,
        data=ClubMemberResponse.model_validate(new_member).model_dump(),
    )


@router.get("/{club_id}/members", summary="Danh sách thành viên câu lạc bộ")
def list_members(
    request: Request,
    club_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Trả về danh sách thành viên cùng role trong câu lạc bộ.
    Chỉ **thành viên** câu lạc bộ mới được xem.
    """
    get_club_or_404(club_id, db)
    require_membership(club_id, current_user, db)

    members = (
        db.query(ClubMember)
        .filter(ClubMember.club_id == club_id)
        .all()
    )

    data = [ClubMemberDetailResponse.model_validate(m).model_dump() for m in members]

    return build_response(
        status_code=200,
        message="Thành công",
        path=request.url.path,
        data=data,
    )


@router.delete("/{club_id}/members/{user_id}", summary="Xóa thành viên khỏi câu lạc bộ")
def remove_member(
    request: Request,
    club_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Xóa thành viên khỏi câu lạc bộ. Chỉ **OWNER** mới có quyền.
    Không được phép xóa OWNER cuối cùng.
    """
    get_club_or_404(club_id, db)
    require_owner(club_id, current_user, db)

    membership = get_membership(club_id, user_id, db)
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Người dùng không phải thành viên của câu lạc bộ này",
        )

    # Bảo vệ: không được xóa OWNER cuối cùng
    if membership.role == ClubRole.OWNER:
        owner_count = (
            db.query(ClubMember)
            .filter(
                ClubMember.club_id == club_id,
                ClubMember.role == ClubRole.OWNER,
            )
            .count()
        )
        if owner_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không thể xóa OWNER cuối cùng của câu lạc bộ",
            )

    db.delete(membership)
    db.commit()

    return build_response(
        status_code=200,
        message="Xóa thành viên thành công",
        path=request.url.path,
        data=None,
    )
