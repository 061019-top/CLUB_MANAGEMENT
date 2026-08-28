from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.db.database import Base, engine
from app.utils.response import build_response 
from app.models.user import User
from app.models.club import Club, ClubMember
from app.models.activity import ClubActivity
# sửa task 18 
from app.dependencies.auth import get_current_user

# task 10 
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.database import get_db

# sửa task 7 
from datetime import datetime






# Handler: Bắt lỗi HTTPException (400, 401, 403, 404...)
async def http_exception_handler(request: Request, exc: HTTPException):
    # sửa task  9
    # if exc.status_code == 404:
    #     return JSONResponse(
    #             status_code=exc.status_code,
    #             content=build_response(
    #                 status_code=exc.status_code,
    #                 message=str(exc.detail),
    #                 path=request.url.path,
    #                 data=None,
    #                 errors=exc.detail,
    #             )
    #         )

    return JSONResponse(
        status_code=exc.status_code,
        content=build_response(
            status_code=exc.status_code,
            message=str(exc.detail),
            path=request.url.path,
            data=None,
            errors=exc.detail,

        )
    )


# Handler: Bắt lỗi validation dữ liệu đầu vào (422)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Trích xuất chỉ lấy phần text thông báo lỗi
    error_messages = [err.get("msg") for err in exc.errors()]
    
    return JSONResponse(
        status_code=422,
        content=build_response(
            status_code=422,
            message="Dữ liệu đầu vào không hợp lệ",
            path=request.url.path,
            data=None, # Nhớ thêm data=None cho đúng cấu trúc
            errors=error_messages # Truyền danh sách các chuỗi text vào đây
        )
    )

# Handler: Bắt mọi lỗi server không mong muốn (500)
async def internal_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=build_response(
            status_code=500,
            message="Lỗi hệ thống, vui lòng thử lại sau",
            path=request.url.path,
            data=None,
            errors=str(exc),
        )
    )

Base.metadata.create_all(bind=engine)

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
)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, internal_exception_handler)

@app.get("/")
def get_api():
    return {"message": "Student Club Management API is running"}

@app.get("/health", tags=["Health Check"])

def health_check():
    return {"status": "ok", "message": "Server is running smoothly!"}
#sửa task 10 
# def health_check(db:Session = Depends(get_db)):
#     count_user = db.query(User).count()
#     return {'count_user': count_user}


#sửa task 18 
@app.get('/verify-token')
def verify_token (
    request: Request,
    current_user: User = Depends(get_current_user)
):
    return JSONResponse(
            status_code=200,
            content=build_response(
                status_code=200,
                message="Lấy token thành công",
                path=request.url.path,
                data ={
                    "valid": True,
                    "user_id": current_user.id
                }, 
            )
        )
    pass

from app.routers import auth, users, club, activity

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(club.router)
app.include_router(activity.router)
