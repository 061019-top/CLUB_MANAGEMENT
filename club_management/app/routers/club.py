from datetime import datetime, timezone
from typing import Annotated
from fastapi import Path
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.models.activity import ClubActivity
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
from app.utils.response import build_response, ApiResponse, Page

router = APIRouter(prefix="/clubs", tags=["Câu lạc bộ"])


from app.services.club import get_club_or_404, get_membership, require_membership, require_owner, record_audit


@router.post("", status_code=status.HTTP_201_CREATED, summary="Tạo câu lạc bộ mới", description='Tạo câu lạc bộ mới. Người tạo tự động trở thành **OWNER**.', response_model=ApiResponse[ClubResponse])
def create_club(
    request: Request,
    club_in: ClubCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    new_club = Club(
        name=club_in.name,
        description=club_in.description,
        owner_id=current_user.id,
    )
    db.add(new_club)
    db.flush()


    owner_membership = ClubMember(
        club_id=new_club.id,
        user_id=current_user.id,
        role=ClubRole.OWNER,
    )
    db.add(owner_membership)
    record_audit(db, new_club.id, current_user.id, 'CLUB_CREATED', club_in.model_dump())
    db.commit()
    db.refresh(new_club)

    return build_response(
        status_code=201,
        message="Tạo câu lạc bộ thành công",
        path=request.url.path,
        data=ClubResponse.model_validate(new_club).model_dump(),
    )


@router.get("", summary="Danh sách câu lạc bộ của tôi", description='Trả về danh sách câu lạc bộ mà user hiện tại là **owner** hoặc **member**.\nHỗ trợ tìm kiếm theo tên.', response_model=ApiResponse[list[ClubResponse]])
def list_clubs(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    search: Optional[str] = Query(None, description="Tìm theo tên câu lạc bộ"),
):

    query = (
        db.query(Club)
        .join(ClubMember, ClubMember.club_id == Club.id)
        .filter(ClubMember.user_id == current_user.id, Club.deleted_at.is_(None))
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


@router.get("/{club_id}", summary="Chi tiết câu lạc bộ", description='Trả về thông tin chi tiết câu lạc bộ. Chỉ **thành viên** câu lạc bộ mới được xem.', response_model=ApiResponse[ClubResponse])
def get_club(
    request: Request,
    club_id: Annotated[int, Path(gt=0, le=2147483647)],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    club = get_club_or_404(club_id, db)
    require_membership(club_id, current_user, db)

    return build_response(
        status_code=200,
        message="Thành công",
        path=request.url.path,
        data=ClubResponse.model_validate(club).model_dump(),
    )


@router.patch("/{club_id}", summary="Cập nhật câu lạc bộ", description='Cập nhật thông tin câu lạc bộ. Chỉ **OWNER** mới có quyền.\nChỉ cập nhật những trường được gửi lên.', response_model=ApiResponse[ClubResponse])
def update_club(
    request: Request,
    club_id: Annotated[int, Path(gt=0, le=2147483647)],
    club_in: ClubUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    club = get_club_or_404(club_id, db)
    require_owner(club_id, current_user, db)

    update_data = club_in.model_dump(exclude_unset=True)
    update_data = {field: value for field, value in update_data.items() if getattr(club, field) != value}
    before = {field: getattr(club, field) for field in update_data}
    if update_data:
        record_audit(db, club_id, current_user.id, 'CLUB_UPDATED', {'before': before, 'after': update_data})
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


@router.delete("/{club_id}", status_code=status.HTTP_200_OK, summary="Xóa câu lạc bộ", response_model=ApiResponse[None], description='Chỉ OWNER được xóa mềm câu lạc bộ. Giữ dữ liệu thành viên, hoạt động và lịch sử; club đã xóa không còn truy cập qua API.')
def delete_club(
    request: Request,
    club_id: Annotated[int, Path(gt=0, le=2147483647)],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    club = get_club_or_404(club_id, db)
    require_owner(club_id, current_user, db)

    club.deleted_at = datetime.now(timezone.utc).replace(tzinfo=None)
    record_audit(db, club_id, current_user.id, 'CLUB_DELETED', {'deleted_at': club.deleted_at.isoformat()})
    db.commit()

    return build_response(
        status_code=200,
        message="Xóa câu lạc bộ thành công",
        path=request.url.path,
        data=None,
    )


@router.post("/{club_id}/members", status_code=status.HTTP_201_CREATED, summary="Thêm thành viên vào câu lạc bộ", description='Thêm một user vào câu lạc bộ với role **MEMBER**. Chỉ **OWNER** mới có quyền.\nKhông cho phép thêm user đã là thành viên.', response_model=ApiResponse[ClubMemberResponse])
def add_member(
    request: Request,
    club_id: Annotated[int, Path(gt=0, le=2147483647)],
    body: AddMemberRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    get_club_or_404(club_id, db)
    require_owner(club_id, current_user, db)


    target_user = db.query(User).filter(User.id == body.user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Người dùng với id={body.user_id} không tồn tại",
        )


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
    record_audit(db, club_id, current_user.id, 'MEMBER_ADDED', {'user_id': body.user_id})
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(400, 'Không thể thêm thành viên: dữ liệu đã thay đổi hoặc thành viên bị trùng')
    db.refresh(new_member)

    return build_response(
        status_code=201,
        message="Thêm thành viên thành công",
        path=request.url.path,
        data=ClubMemberResponse.model_validate(new_member).model_dump(),
    )


@router.get("/{club_id}/members", summary="Danh sách thành viên câu lạc bộ", description='Trả về danh sách thành viên cùng role trong câu lạc bộ.\nChỉ **thành viên** câu lạc bộ mới được xem.', response_model=ApiResponse[list[ClubMemberDetailResponse]])
def list_members(
    request: Request,
    club_id: Annotated[int, Path(gt=0, le=2147483647)],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

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


@router.delete("/{club_id}/members/{user_id}", summary="Xóa thành viên khỏi câu lạc bộ", description='Xóa thành viên khỏi câu lạc bộ. Chỉ **OWNER** mới có quyền.\nKhông được phép xóa OWNER cuối cùng.', response_model=ApiResponse[None])
def remove_member(
    request: Request,
    club_id: Annotated[int, Path(gt=0, le=2147483647)],
    user_id: Annotated[int, Path(gt=0, le=2147483647)],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    get_club_or_404(club_id, db)
    require_owner(club_id, current_user, db)

    membership = get_membership(club_id, user_id, db)
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Người dùng không phải thành viên của câu lạc bộ này",
        )


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

    db.query(ClubActivity).filter(ClubActivity.club_id == club_id, ClubActivity.assignee_id == user_id).update({"assignee_id": None}, synchronize_session=False)
    db.delete(membership)
    record_audit(db, club_id, current_user.id, 'MEMBER_REMOVED', {'user_id': user_id})
    db.commit()

    return build_response(
        status_code=200,
        message="Xóa thành viên thành công",
        path=request.url.path,
        data=None,
    )
