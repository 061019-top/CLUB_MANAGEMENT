from typing import Annotated
from fastapi import Path
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import Optional, Literal
from sqlalchemy import desc

from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.club import Club, ClubMember, ClubRole
from app.models.activity import ClubActivity, ActivityStatus, ActivityPriority
from app.schemas.activity import ActivityCreate, ActivityUpdate, ActivityResponse
from app.utils.response import build_response, ApiResponse, Page

router = APIRouter(tags=["Hoạt động câu lạc bộ"])


from app.services.club import get_club_or_404, get_membership, require_membership, require_owner


def get_activity_or_404(activity_id: int, db: Session) -> ClubActivity:

    activity = db.query(ClubActivity).filter(ClubActivity.id == activity_id).first()
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hoạt động câu lạc bộ với id={activity_id} không tồn tại",
        )
    return activity


@router.post("/clubs/{club_id}/activities", status_code=status.HTTP_201_CREATED, summary="Tạo hoạt động câu lạc bộ", description='Tạo hoạt động câu lạc bộ. Chỉ **thành viên** câu lạc bộ mới được tạo.\nGán assignee phải là thành viên câu lạc bộ.', response_model=ApiResponse[ActivityResponse])
def create_activity(
    request: Request,
    club_id: Annotated[int, Path(gt=0, le=2147483647)],
    activity_in: ActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    get_club_or_404(club_id, db)

    require_membership(club_id, current_user, db)


    if activity_in.assignee_id is not None:
        assignee_membership = get_membership(club_id, activity_in.assignee_id, db)
        if not assignee_membership or not assignee_membership.user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Người được giao (assignee) phải là thành viên đang hoạt động của câu lạc bộ",
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


@router.get("/clubs/{club_id}/activities", summary="Danh sách hoạt động câu lạc bộ", description='Trả về danh sách hoạt động câu lạc bộ thuộc câu lạc bộ, phân trang, lọc và tìm kiếm.\nChỉ **thành viên** mới xem được.', response_model=ApiResponse[Page[ActivityResponse]])
def list_activities(
    request: Request,
    club_id: Annotated[int, Path(gt=0, le=2147483647)],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status_filter: Optional[ActivityStatus] = Query(None, alias="status", description="Lọc theo trạng thái (TODO, IN_PROGRESS, DONE)"),
    priority_filter: Optional[ActivityPriority] = Query(None, alias="priority", description="Lọc theo độ ưu tiên (LOW, MEDIUM, HIGH)"),
    assignee_id: Optional[int] = Query(None, description="Lọc theo ID người được giao"),
    search: Optional[str] = Query(None, description="Tìm theo tiêu đề (title)"),
    limit: int = Query(20, ge=1, le=100, description="Số lượng kết quả lấy ra"),
    offset: int = Query(0, ge=0, description="Số lượng kết quả muốn bỏ qua từ đầu"),
    sort_by: Literal["created_at", "due_date"] = Query("created_at", description="Trường sắp xếp"),
    sort_order: Literal["asc", "desc"] = Query("desc", description="Chiều sắp xếp"),
):


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


    column = getattr(ClubActivity, sort_by)
    ordering = column.asc() if sort_order == "asc" else column.desc()
    query = query.order_by(column.is_(None), ordering, ClubActivity.id.asc() if sort_order == "asc" else ClubActivity.id.desc())


    total = query.count()
    activities = query.offset(offset).limit(limit).all()


    data = [ActivityResponse.model_validate(act).model_dump() for act in activities]

    return build_response(
        status_code=200,
        message="Thành công",
        path=request.url.path,
        data={
            "items": data,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    )


@router.get("/activities/{activity_id}", summary="Chi tiết hoạt động câu lạc bộ", description='Trả về chi tiết hoạt động câu lạc bộ.\nChỉ cho phép nếu user là **thành viên** của câu lạc bộ chứa hoạt động đó.', response_model=ApiResponse[ActivityResponse])
def get_activity(
    request: Request,
    activity_id: Annotated[int, Path(gt=0, le=2147483647)],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):


    activity = get_activity_or_404(activity_id, db)


    require_membership(activity.club_id, current_user, db)

    return build_response(
        status_code=200,
        message="Thành công",
        path=request.url.path,
        data=ActivityResponse.model_validate(activity).model_dump(),
    )


@router.patch("/activities/{activity_id}", summary="Cập nhật hoạt động câu lạc bộ", response_model=ApiResponse[ActivityResponse], description='OWNER cập nhật các trường hợp lệ; assignee chỉ cập nhật status. Trường không gửi được giữ nguyên; title/status/priority không nhận null.')
def update_activity(
    request: Request,
    activity_id: Annotated[int, Path(gt=0, le=2147483647)],
    activity_in: ActivityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    activity = get_activity_or_404(activity_id, db)
    membership = require_membership(activity.club_id, current_user, db)


    update_data = activity_in.model_dump(exclude_unset=True)

    if membership.role == ClubRole.OWNER:
        if "assignee_id" in update_data and update_data["assignee_id"] is not None:
            assignee_membership = get_membership(activity.club_id, update_data["assignee_id"], db)
            if not assignee_membership or not assignee_membership.user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Người được giao (assignee) phải là thành viên đang hoạt động của câu lạc bộ",
                )

        for field, value in update_data.items():
            setattr(activity, field, value)

    elif activity.assignee_id == current_user.id:

        if set(update_data.keys()) != {'status'}:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Người được giao (assignee) chỉ được cập nhật status",
            )

        activity.status = update_data['status']

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền cập nhật hoạt động này"
        )


    db.commit()
    db.refresh(activity)

    return build_response(
        status_code=200,
        message="Cập nhật hoạt động câu lạc bộ thành công",
        path=request.url.path,
        data=ActivityResponse.model_validate(activity).model_dump(),
    )


@router.delete("/activities/{activity_id}", summary="Xóa hoạt động câu lạc bộ", description='Xóa hoạt động câu lạc bộ. Chỉ **OWNER** mới có quyền xóa.', response_model=ApiResponse[None])
def delete_activity(
    request: Request,
    activity_id: Annotated[int, Path(gt=0, le=2147483647)],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

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
