from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.db.database import Base, engine
from app.utils.response import build_response # noqa: F401 – re-exported for routers
from app.models.user import User
from app.models.club import Club, ClubMember
from app.models.activity import ClubActivity 

# Handler: Bắt lỗi HTTPException (400, 401, 403, 404...)
async def http_exception_handler(request: Request, exc: HTTPException):
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
    return JSONResponse(
        status_code=422,
        content=build_response(
            status_code=422,
            message="Dữ liệu đầu vào không hợp lệ",
            path=request.url.path,
            errors=exc.errors()
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

app = FastAPI(title="Student Club Management API", version="1.0.0")

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, internal_exception_handler)

from app.routers import auth, users, club  # noqa: E402 – import after app creation to avoid circular imports

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(club.router)
