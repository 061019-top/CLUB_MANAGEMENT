from app.services.auth import register_user, login_user, refresh_tokens
from app.services.rate_limit import limit_login
from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import LoginRequest, RefreshRequest, Token
from app.utils.response import build_response, ApiResponse, Page

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", status_code=status.HTTP_201_CREATED , summary="Đăng ký", response_model=ApiResponse[UserResponse], description='Đăng ký USER; email duy nhất, mật khẩu bcrypt, không trả password_hash.')
def register(request: Request, user_in: UserCreate, db: Session = Depends(get_db)):
    new_user = register_user(db, user_in)

    return build_response(
        status_code=201,
        message="Đăng ký tài khoản thành công",
        path=request.url.path,
        data=UserResponse.model_validate(new_user).model_dump(),

    )

@router.post("/login", summary="Đăng nhập", dependencies=[Depends(limit_login)], response_model=ApiResponse[Token], description='Đăng nhập JSON email/password; sao chép data.access_token vào Authorize. Giới hạn tần suất theo IP.')
def login(request: Request, login_data: LoginRequest, db: Session = Depends(get_db)):
    token = login_user(db, str(login_data.email), login_data.password)

    return build_response(
        status_code=200,
        message="Đăng nhập thành công",
        path=request.url.path,
        data=token,


    )


@router.post('/refresh', summary='Cấp lại token bằng refresh JWT', response_model=ApiResponse[Token], description='Cấp cặp JWT mới bằng refresh JWT còn hạn; kiểm tra tài khoản đang hoạt động.')
def refresh(request: Request, body: RefreshRequest, db: Session = Depends(get_db)):
    return build_response(status_code=200, message='Cấp lại token thành công',
                          path=request.url.path, data=refresh_tokens(db, body.refresh_token))
