# Worksheet

|CẤU TRÚC THƯ MỤC FASTAPI GỢI Ý — STUDENT CLUB MANAGEMENT API| |
|---|---|
| | |
|Đường dẫn|Ý nghĩa|
|club_management/|Thư mục gốc dự án|
|app/|Mã nguồn chính|
|app/main.py|Khởi tạo FastAPI app, include routers, middleware|
|app/core/|Cấu hình dùng chung|
|app/core/config.py|Đọc biến môi trường và settings|
|app/core/security.py|Hash password, JWT encode/decode|
|app/db/|Kết nối và session database|
|app/db/database.py|engine, SessionLocal, Base, get_db|
|app/models/|SQLAlchemy models|
|app/models/user.py|Model User|
|app/models/club.py|Model Club / ClubMember|
|app/models/activity.py|Model ClubActivity|
|app/schemas/|Pydantic request/response schemas|
|app/routers/|FastAPI APIRouter theo module|
|app/routers/auth.py|Register/Login|
|app/routers/users.py|User endpoints|
|app/routers/club.py|Câu lạc bộ/Member endpoints|
|app/routers/activity.py|Hoạt động câu lạc bộ endpoints|
|app/services/|Nghiệp vụ và thao tác dữ liệu|
|app/dependencies/|get_current_user, role/permission dependencies|
|app/utils/|Helper dùng chung|
|tests/|Test API/service|
|.env.example|Mẫu biến môi trường, không chứa secret thật|
|requirements.txt|Danh sách thư viện|
|README.md|Cách cài đặt, chạy và demo|
