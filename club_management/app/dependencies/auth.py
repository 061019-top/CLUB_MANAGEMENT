from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.database import get_db
from app.models.user import User, UserRole


security = HTTPBearer(auto_error=False, bearerFormat='JWT')

def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(security), db: Session = Depends(get_db)):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác thực thông tin đăng nhập",
        headers={"WWW-Authenticate": "Bearer"},
    )


    if not credentials:
        raise credentials_exception


    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM], options={'require_exp': True, 'require_sub': True})
        user_id: str = payload.get("sub")
        if payload.get('type') != 'access':
            raise credentials_exception
        if not isinstance(user_id, str) or not user_id.isdecimal() or len(user_id) > 10:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tài khoản đang bị khóa hoặc không hoạt động")

    return user

def get_current_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không đủ quyền truy cập"
        )
    return current_user
