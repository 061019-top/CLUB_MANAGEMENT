from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from app.utils.response import build_response, ERROR_RESPONSES, HealthResponse
from sqlalchemy.exc import IntegrityError, DataError


async def http_exception_handler(request: Request, exc: HTTPException):

    return JSONResponse(
        status_code=exc.status_code,
        headers=exc.headers,
        content=build_response(
            status_code=exc.status_code,
            message=str(exc.detail),
            path=request.url.path,
            data=None,
            errors=exc.detail,

        )
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_messages = [err.get("msg") for err in exc.errors()]

    return JSONResponse(
        status_code=422,
        content=build_response(
            status_code=422,
            message="Dữ liệu đầu vào không hợp lệ",
            path=request.url.path,
            data=None,
            errors=error_messages
        )
    )


async def internal_exception_handler(request: Request, exc: Exception):
    logging.getLogger(__name__).error('Unhandled API error', exc_info=exc)
    return JSONResponse(
        status_code=500,
        content=build_response(
            status_code=500,
            message="Lỗi hệ thống, vui lòng thử lại sau",
            path=request.url.path,
            data=None,
            errors=None,
        )
    )


tags_metadata = [
    {
        "name": "Auth",
        "description": "Quản lý đăng ký, đăng nhập và cấp phát token JWT.",
    },
    {
        "name": "User",
        "description": "Quản lý thông tin hồ sơ và danh sách người dùng.",
    },
    {
        "name": "Câu lạc bộ",
        "description": "Quản lý câu lạc bộ và thành viên câu lạc bộ.",
    },
    {
        "name": "Hoạt động câu lạc bộ",
        "description": "Quản lý các hoạt động, sự kiện, công việc trong câu lạc bộ.",
    },
]

app = FastAPI(
    title="Student Club Management API",
    description="API quản lý câu lạc bộ sinh viên: Tạo câu lạc bộ, quản lý thành viên, và phân công hoạt động.",
    version="1.0.0",
    openapi_tags=tags_metadata,
    responses=ERROR_RESPONSES,
)

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, internal_exception_handler)


async def database_constraint_handler(request: Request, exc: Exception):
    return await http_exception_handler(request, HTTPException(400, 'Dữ liệu vi phạm ràng buộc database hoặc đã bị thay đổi'))


app.add_exception_handler(IntegrityError, database_constraint_handler)
app.add_exception_handler(DataError, database_constraint_handler)

@app.get("/health", tags=["Health Check"], response_model=HealthResponse, summary="Kiểm tra API", description="Kiểm tra tiến trình API đang hoạt động.")

def health_check():
    return {"status": "ok", "message": "Server is running smoothly!"}


from app.routers import auth, users, club, activity

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(club.router)
app.include_router(activity.router)
