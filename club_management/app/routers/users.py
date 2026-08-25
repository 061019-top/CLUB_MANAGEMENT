from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.schemas.user import UserResponse
from app.models.user import User
from app.dependencies.auth import get_current_user, get_current_admin
from app.utils.response import build_response

router = APIRouter(prefix="/users", tags=["User"])

@router.get("/me")
def read_users_me(request: Request, current_user: User = Depends(get_current_user)):
    return build_response(
        status_code=200,
        message="Thành công",
        path=request.url.path,
        data=UserResponse.model_validate(current_user).model_dump(),
    )

@router.get("")
def read_users(
    request: Request,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
    search: Optional[str] = Query(None, description="Tìm theo tên hoặc email"),
    is_active: Optional[bool] = Query(None, description="Lọc theo trạng thái hoạt động")
):
    query = db.query(User)

    if search:
        search_filter = f"%{search}%"
        query = query.filter((User.full_name.ilike(search_filter)) | (User.email.ilike(search_filter)))

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    users = query.all()
    data = [UserResponse.model_validate(u).model_dump() for u in users]

    return build_response(
        status_code=200,
        message="Thành công",
        path=request.url.path,
        data=data,
    )
