from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import get_password_hash, verify_password, create_access_token
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from jose import jwt, JWTError
from app.core.config import settings


def issue_tokens(user: User):
    refresh = jwt.encode({'sub': str(user.id), 'type': 'refresh', 'jti': uuid4().hex,
                          'exp': datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)},
                         settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return {'access_token': create_access_token({'sub': str(user.id)}),
            'refresh_token': refresh, 'token_type': 'bearer'}


def refresh_tokens(db: Session, token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM],
                             options={'require_exp': True, 'require_sub': True})
        subject = payload.get('sub')
        if payload.get('type') != 'refresh' or not isinstance(subject, str) or not subject.isdecimal() or len(subject) > 10:
            raise JWTError('Invalid refresh token')
    except JWTError:
        raise HTTPException(401, 'Refresh token không hợp lệ hoặc hết hạn', headers={'WWW-Authenticate': 'Bearer'})
    user = db.get(User, int(subject))
    if user is None:
        raise HTTPException(401, 'Người dùng không tồn tại', headers={'WWW-Authenticate': 'Bearer'})
    if not user.is_active:
        raise HTTPException(403, 'Tài khoản đang bị khóa hoặc không hoạt động')
    return issue_tokens(user)


def register_user(db: Session, data):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(400, 'Email đã được đăng ký')
    user = User(email=data.email, full_name=data.full_name,
                password_hash=get_password_hash(data.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(400, 'Email đã được đăng ký')
    db.refresh(user)
    return user


def login_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email.lower()).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(401, 'Email hoặc mật khẩu không chính xác',
                            headers={'WWW-Authenticate': 'Bearer'})
    if not user.is_active:
        raise HTTPException(403, 'Tài khoản đang bị khóa hoặc không hoạt động')
    return issue_tokens(user)
