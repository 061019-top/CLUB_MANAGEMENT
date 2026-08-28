from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import LoginRequest, Token
from app.models.user import User
from app.core.security import get_password_hash, verify_password, create_access_token
from datetime import timedelta
from app.core.config import settings
from app.utils.response import build_response

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(request: Request, user_in: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã được đăng ký"
        )
    #TODO
    # sửa task 16
    if len(user_in.full_name.strip().split()) < 2:
        raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=" full_name phải có ít nhất 2 từ chứa dấu cách"
                )
    # sửa code 2 
    kitu ='@#$%!'
    check_kitu = 0

    for chu in user_in.password:
        if chu in kitu:
            check_kitu = 1
            break

    if len(user_in.password.strip()) < 8 or check_kitu == 0:
         raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Mật khẩu phải có 8 kí tự và có kí tự đặc biệt là {kitu}"
                )   


    #TODO

    hashed_password = get_password_hash(user_in.password)
    new_user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        password_hash=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return build_response(
        status_code=201,
        message="Đăng ký tài khoản thành công",
        path=request.url.path,
        #data=UserResponse.model_validate(new_user).model_dump(),

        #sửa code 1 
        data = {
            'id' : new_user.id,
            'email': new_user.email
        }
    )

@router.post("/login")
def login(request: Request, login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        # raise HTTPException(
        #     status_code=status.HTTP_401_UNAUTHORIZED,
        #     detail="Email hoặc mật khẩu không chính xác",
        #     headers={"WWW-Authenticate": "Bearer"},
        # )
        # sửa code 5 
        raise HTTPException (
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Sai thông tin đăng nhập",
            headers={"WWW-Authenticate": "Bearer"}, 
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tài khoản đang bị khóa hoặc không hoạt động")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    return build_response(
        status_code=200,
        message="Đăng nhập thành công",
        path=request.url.path,
        #data={"access_token": access_token, "token_type": "bearer"},

        # sửa code 3 
        data={"access_token": access_token, "token_type": "bearer", 'id':user.id, 'email':user.email, 'role': user.role},

    )
