import bcrypt
from datetime import datetime, timedelta, timezone
from jose import jwt
from app.core.config import settings

def check_password_length(password: str) -> str:
    if len(password) < 8 or len(password.encode('utf-8')) > 72:
        raise ValueError('Mật khẩu cần ít nhất 8 ký tự và không quá 72 byte; hãy rút ngắn nếu quá dài.')
    return password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        if len(plain_password.encode('utf-8')) > 72:
            return False
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except ValueError:
        return False

def get_password_hash(password: str) -> str:
    check_password_length(password)
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta is not None:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
