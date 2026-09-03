from typing import Generic, TypeVar
from pydantic import BaseModel
from datetime import datetime


def build_response(status_code: int, message: str, path: str = "", data=None, errors=None):
    return {
        "status_code": status_code,
        "message": message,
        "path": path,
        "data": data,
        "errors": errors,
        "timestamp": datetime.now().isoformat(),
    }


T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    status_code: int
    message: str
    path: str
    data: T
    errors: str | list[str] | None = None
    timestamp: datetime


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    limit: int
    offset: int


class HealthResponse(BaseModel):
    status: str
    message: str


ERROR_RESPONSES = {
    code: {'model': ApiResponse[None], 'description': message}
    for code, message in {
        400: 'Dữ liệu không phù hợp quy tắc nghiệp vụ hoặc xung đột dữ liệu',
        401: 'Thiếu token, token sai hoặc hết hạn',
        403: 'Không đủ quyền hoặc tài khoản bị khóa',
        404: 'Không tìm thấy tài nguyên',
        422: 'Dữ liệu đầu vào không hợp lệ',
        429: 'Vượt hạn mức đăng nhập; xem Retry-After',
        500: 'Lỗi hệ thống không mong đợi',
    }.items()
}
