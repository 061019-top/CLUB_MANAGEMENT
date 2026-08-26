from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from sqlalchemy import desc

from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.club import Club, ClubMember, ClubRole
from app.models.activity import ClubActivity, ActivityStatus, ActivityPriority
from app.schemas.activity import ActivityCreate, ActivityUpdate, ActivityResponse
from app.utils.response import build_response

router = APIRouter(tags=["Hoạt động câu lạc bộ"])

def get_club_or_404(club_id: int, db: Session) -> Club:
    club = db.query(Club).filter(Club.id == club_id).first()
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
    membership = get_membership(club_id, user.id, db)
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền truy cập vì không phải thành viên của câu lạc bộ này",
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

def get_activity_or_404(activity_id: int, db: Session) -> ClubActivity:
    activity = db.query(ClubActivity).filter(ClubActivity.id == activity_id).first()
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hoạt động câu lạc bộ với id={activity_id} không tồn tại",
        )
    return activity


@router.post("/clubs/{club_id}/activities", status_code=status.HTTP_201_CREATED, summary="Tạo hoạt động câu lạc bộ")
def create_activity(
    request: Request,
    club_id: int,
    activity_in: ActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Tạo hoạt động câu lạc bộ. Chỉ **thành viên** câu lạc bộ mới được tạo.
    Gán assignee phải là thành viên câu lạc bộ.
    """
    get_club_or_404(club_id, db)
    require_membership(club_id, current_user, db)

    if activity_in.assignee_id is not None:
        assignee_membership = get_membership(club_id, activity_in.assignee_id, db)
        if not assignee_membership:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Người được giao (assignee) phải là thành viên của câu lạc bộ",
            )

    new_activity = ClubActivity(
        club_id=club_id,
        title=activity_in.title,
        description=activity_in.description,
        assignee_id=activity_in.assignee_id,
        status=activity_in.status,
        priority=activity_in.priority,
        due_date=activity_in.due_date,
    )
    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)

    return build_response(
        status_code=201,
        message="Tạo hoạt động câu lạc bộ thành công",
        path=request.url.path,
        data=ActivityResponse.model_validate(new_activity).model_dump(),
    )


@router.get("/clubs/{club_id}/activities", summary="Danh sách hoạt động câu lạc bộ")
def list_activities(
    request: Request,
    club_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status_filter: Optional[ActivityStatus] = Query(None, alias="status", description="Lọc theo trạng thái (TODO, IN_PROGRESS, DONE)"),
    priority_filter: Optional[ActivityPriority] = Query(None, alias="priority", description="Lọc theo độ ưu tiên (LOW, MEDIUM, HIGH)"),
    assignee_id: Optional[int] = Query(None, description="Lọc theo ID người được giao"),
    search: Optional[str] = Query(None, description="Tìm theo tiêu đề (title)"),
    page: int = Query(1, ge=1, description="Số trang (bắt đầu từ 1)"),
    size: int = Query(20, ge=1, le=100, description="Kích thước trang"),
):
    """
    Trả về danh sách hoạt động câu lạc bộ thuộc câu lạc bộ, phân trang, lọc và tìm kiếm.
    Chỉ **thành viên** mới xem được.
    """
    get_club_or_404(club_id, db)
    require_membership(club_id, current_user, db)

    query = db.query(ClubActivity).filter(ClubActivity.club_id == club_id)

    if status_filter:
        query = query.filter(ClubActivity.status == status_filter)
    if priority_filter:
        query = query.filter(ClubActivity.priority == priority_filter)
    if assignee_id:
        query = query.filter(ClubActivity.assignee_id == assignee_id)
    if search:
        query = query.filter(ClubActivity.title.ilike(f"%{search}%"))

    # Sorting
    query = query.order_by(desc(ClubActivity.created_at))

    # Pagination
    total = query.count()
    offset = (page - 1) * size
    activities = query.offset(offset).limit(size).all()

    data = [ActivityResponse.model_validate(act).model_dump() for act in activities]

    return build_response(
        status_code=200,
        message="Thành công",
        path=request.url.path,
        data={
            "items": data,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
    )


@router.get("/activities/{activity_id}", summary="Chi tiết hoạt động câu lạc bộ")
def get_activity(
    request: Request,
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Trả về chi tiết hoạt động câu lạc bộ.
    Chỉ cho phép nếu user là **thành viên** của câu lạc bộ chứa hoạt động đó.
    """
    activity = get_activity_or_404(activity_id, db)
    require_membership(activity.club_id, current_user, db)

    return build_response(
        status_code=200,
        message="Thành công",
        path=request.url.path,
        data=ActivityResponse.model_validate(activity).model_dump(),
    )


@router.patch("/activities/{activity_id}", summary="Cập nhật hoạt động câu lạc bộ")
def update_activity(
    request: Request,
    activity_id: int,
    activity_in: ActivityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Cập nhật hoạt động câu lạc bộ. 
    Người dùng phải là OWNER hoặc Assignee của hoạt động này.
    Không ghi đè trường không gửi lên.
    """
    activity = get_activity_or_404(activity_id, db)
    membership = require_membership(activity.club_id, current_user, db)

    # Theo Spec: "Theo permission". Ta gán: OWNER hoặc Assignee mới được phép.
    if membership.role != ClubRole.OWNER and activity.assignee_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền cập nhật hoạt động này (chỉ OWNER hoặc Assignee mới có quyền)"
        )

    update_data = activity_in.model_dump(exclude_unset=True)

    if "assignee_id" in update_data and update_data["assignee_id"] is not None:
        assignee_membership = get_membership(activity.club_id, update_data["assignee_id"], db)
        if not assignee_membership:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Người được giao (assignee) phải là thành viên của câu lạc bộ",
            )

    for field, value in update_data.items():
        setattr(activity, field, value)

    db.commit()
    db.refresh(activity)

    return build_response(
        status_code=200,
        message="Cập nhật hoạt động câu lạc bộ thành công",
        path=request.url.path,
        data=ActivityResponse.model_validate(activity).model_dump(),
    )


@router.delete("/activities/{activity_id}", summary="Xóa hoạt động câu lạc bộ")
def delete_activity(
    request: Request,
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Xóa hoạt động câu lạc bộ. Chỉ **OWNER** mới có quyền xóa.
    """
    activity = get_activity_or_404(activity_id, db)
    require_owner(activity.club_id, current_user, db)

    db.delete(activity)
    db.commit()

    return build_response(
        status_code=200,
        message="Xóa hoạt động câu lạc bộ thành công",
        path=request.url.path,
        data=None,
    )
