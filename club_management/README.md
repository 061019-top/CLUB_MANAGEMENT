# Student Club Management API

Hoàn thiện 36 task bắt buộc của 5 tiết theo danh_sach_task.md, to_chuc_du_lieu.md,
dac_ta_api.md và cau_truc_thu_muc.md. HTTP Bearer được giữ theo yêu cầu của chủ dự án,
thay cho OAuth2PasswordBearer được nêu ở task Current user.

## Cài đặt và chạy

Chạy lệnh trong thư mục club_management, dùng Python 3.12 trở lên:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

requirements.txt chứa thư viện chạy ứng dụng. Không đưa .venv/, cache hoặc .env lên Git.
Nếu thư mục dự án đã đổi tên, dùng python.exe -m uvicorn như bên dưới để tránh
launcher uvicorn.exe còn chứa đường dẫn cũ.

Nếu chưa có .env, sao chép .env.example thành .env. Điền DATABASE_URL của MySQL và
SECRET_KEY ngẫu nhiên ít nhất 32 ký tự, giữ ALGORITHM=HS256. Có thể tạo secret bằng:

```powershell
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(48))"
```

Tạo database trong MySQL nếu chưa có:

```sql
CREATE DATABASE IF NOT EXISTS club_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

```powershell
.\.venv\Scripts\python.exe -m app.db.database
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

initialize_database tạo bảng còn thiếu, bổ sung clubs.deleted_at và index nếu chưa có, rồi kiểm
tra schema. Đây là migration cộng thêm cho task 27–28 đã được duyệt; không xóa dữ liệu.
Chạy lại được. MySQL DDL tự commit, nên chạy lệnh này bằng một tiến trình khi cập nhật
phiên bản, trước khi khởi động API. Schema gồm bốn bảng gốc và audit_logs theo phần
bổ sung trong to_chuc_du_lieu.md. MySQL hiện tại đã được cập nhật thành công.

## Đăng nhập bằng HTTP Bearer

1. Mở http://127.0.0.1:8000/docs.
2. Tạo tài khoản tại POST /auth/register (email, full_name, password).
3. Gọi POST /auth/login bằng JSON email/password.
4. Sao chép data.access_token, bấm Authorize và dán vào Value, không thêm chữ Bearer.
5. Gọi các API bảo vệ. Ngoài Swagger, gửi header Authorization: Bearer <access_token>.

Không có /auth/token. Đăng ký luôn tạo USER, không nhận role từ client.
Mật khẩu tối thiểu 8 ký tự và tối đa 72 byte UTF-8, lưu bằng bcrypt.
Quản trị database có thể cấp ADMIN cho tài khoản mong muốn bằng trường role có sẵn:

```sql
UPDATE users SET role = 'ADMIN' WHERE email = 'admin@example.com';
```

## API và quyền

- GET /health kiểm tra tiến trình API theo task health-check tiết 1.
- POST /auth/register, POST /auth/login: công khai.
- GET /users/me: user đăng nhập; GET /users: ADMIN, search tên/email, is_active,
  limit (1–50), offset.
- POST /clubs: tạo club và membership OWNER trong cùng transaction.
- GET /clubs: chỉ club của người gọi, hỗ trợ search tên.
- GET /clubs/{club_id}: thành viên xem; PATCH và DELETE: chỉ OWNER.
- POST /clubs/{club_id}/members: OWNER thêm thành viên; GET: thành viên xem.
- DELETE /clubs/{club_id}/members/{user_id}: OWNER, không xóa OWNER cuối cùng;
  bỏ assignee của các hoạt động được giao cho người vừa rời club.
- POST /clubs/{club_id}/activities: thành viên tạo, assignee phải thuộc club và có
  tài khoản is_active=true. GET cùng URL: list/filter/search/phân trang/sắp xếp.
- GET /activities/{activity_id}: thành viên xem; PATCH: OWNER sửa các trường hợp lệ,
  assignee chỉ sửa status; DELETE: chỉ OWNER.

Xóa club là xóa mềm: gán clubs.deleted_at theo UTC, giữ membership, hoạt động và log.
Club đã xóa bị ẩn khỏi danh sách; API club/member/activity trả 404, kể cả truy cập bằng
activity_id. Không có endpoint khôi phục, xóa vĩnh viễn hoặc xem log. Danh sách API
và HTTP Bearer giữ nguyên; refresh không cần bảng refresh_tokens.

PATCH chỉ thay đổi trường gửi lên; title/name/status/priority không nhận null.
description, assignee_id, due_date cho phép null khi phù hợp entity.
Tên/tiêu đề tối đa 255 ký tự; mô tả tuân giới hạn TEXT MySQL 65535 byte.
Ngày có timezone được chuyển sang UTC trước khi lưu DATETIME.

Danh sách hoạt động hỗ trợ kết hợp status, priority, assignee_id, search;
limit (1–100), offset; sort_by=created_at hoặc due_date, sort_order=asc hoặc desc.
Mặc định created_at giảm dần. Hạn xử lý null nằm cuối, id dùng phân định khi trùng ngày.

Response giữ format status_code, message, path, data, errors, timestamp. Swagger có
response model cụ thể và mô tả status code. 400: vi phạm nghiệp vụ; 401: sai/thiếu/hết
hạn token; 403: thiếu quyền/user khóa; 404: không tồn tại; 422: validation; 429: rate limit.
Không trả password_hash. Lỗi hệ thống không trả chi tiết database cho client.

## Phần không bắt buộc còn tương thích đặc tả

- Seed dữ liệu: chạy .\.venv\Scripts\python.exe -m app.db.seed --password 'DemoPassword123!'.
  Tạo 3 tài khoản admin@example.com, owner@example.com, member@example.com;
  2 club, 4 membership, 6 hoạt động. Chạy lại giữ tài khoản/club đã tồn tại;
  mật khẩu chỉ áp dụng cho tài khoản mới. Không khôi phục club đã xóa mềm; không ghi
  log trùng khi seed lại. Chỉ chạy seed trên DB demo.
- POST /auth/refresh nhận JSON {"refresh_token": "<token>"}, trả cặp token tại data.
  Refresh là JWT có chữ ký và hạn dùng REFRESH_TOKEN_EXPIRE_DAYS (mặc định 7 ngày),
  phân biệt type=refresh với access token. Không lưu bảng refresh token: token cũ
  còn sử dụng được đến khi hết hạn, chưa có thu hồi từng token/rotation một lần dùng.
  Kiểm tra user tồn tại và hoạt động ở mỗi lần refresh.
- Login giới hạn LOGIN_RATE_LIMIT (mặc định 10 lần/IP) trong
  LOGIN_RATE_WINDOW_SECONDS (mặc định 60 giây), trả 429 và Retry-After.
  Bộ đếm RAM phù hợp demo một tiến trình, reset khi restart và không chia sẻ nhiều worker.

## Kiểm tra và lịch sử kiểm thử

Theo yêu cầu mới, đã bỏ tests/ và requirements-dev.txt. Dùng checklist Swagger/Postman
trong test_checklist.md để kiểm tra thủ công; các số liệu tự động dưới đây là kết quả
trước khi xóa bộ test, không phải bộ test còn có trong phiên bản hiện tại.


Kết quả 08/09/2026: 35 test đạt trên SQLite có khóa ngoại. Đã kiểm thử tích hợp trên
MySQL hiện tại bằng transaction rollback: auth, ADMIN, club/member/activity, quyền,
PATCH null, filter/sort và Swagger; xác nhận không còn user test sau rollback.
initialize_database đã cập nhật và xác nhận năm bảng trên MySQL, gồm audit_logs. Có 2 cảnh báo deprecation từ thư viện
TestClient, không ảnh hưởng kết quả kiểm thử.

Xem test_checklist.md để đối chiếu 36 task, các lỗi đã sửa và checklist thao tác API.
Task bonus 27 (Activity log) và 28 (Soft delete) đã hoàn thiện theo phần bổ sung
được chủ dự án duyệt. Bonus comment/attachment của tiết 4 chưa triển khai. .env đã được Git theo dõi từ trước cần được bỏ theo dõi trước
khi chia sẻ repository; .gitignore không tự loại file đã được theo dõi.


## Activity log — task 27

Model AuditLog nằm trong app/models/club.py; ghi log từ app/services/club.py.
Tạo/sửa/xóa club và thêm/xóa member ghi actor_id, club_id, action, details, created_at.
CLUB_UPDATED chứa before/after; log member chứa user_id; log xóa mềm chứa deleted_at.
PATCH không thay đổi dữ liệu và các yêu cầu thất bại không sinh log. Ghi log cùng
transaction nghiệp vụ: nếu ghi log lỗi thì thay đổi club/member cũng rollback.
Không lưu mật khẩu hay JWT trong log. Log bắt đầu từ khi triển khai, không dựng lại
lịch sử các thao tác đã xảy ra trước đó.

Không thêm API xem log. Đọc trong MySQL bằng tài khoản quản trị:

```sql
SELECT id, club_id, actor_id, action, details, created_at
FROM audit_logs
ORDER BY id DESC
LIMIT 100;
```

Kiểm tra dữ liệu đã xóa mềm:

```sql
SELECT id, name, deleted_at FROM clubs WHERE deleted_at IS NOT NULL;
```

Đã kiểm thử rollback khi ghi log thất bại cho cả 5 loại thao tác; xóa mềm giữ nguyên
member/activity và chặn mọi đường truy cập liên quan. Migration được chạy hai lần
trên MySQL và kiểm tra giá trị các dòng cũ không thay đổi. Luồng tích hợp MySQL cho
task 27–28 đạt; rollback xác nhận không còn user/club/log test.


## Cách đọc code seed và database

Trong app/db/seed.py, đọc hàm seed trước:

1. check_password_length kiểm tra mật khẩu bằng một câu if.
2. create_demo_user tạo ba tài khoản. Email đã có thì trả về user cũ.
3. create_demo_club tạo câu lạc bộ. Club đã có thì bỏ qua, kể cả club đã xóa mềm.
4. add_demo_members thêm owner và member vào club mới.
5. create_demo_activities tạo ba hoạt động với trạng thái/độ ưu tiên rõ ràng.

Hàm main đọc --password rồi mở phiên làm việc bằng SessionLocal(). Sau khi seed
thành công, db.commit() lưu toàn bộ dữ liệu. Nếu có lỗi, db.rollback() hủy thay đổi
chưa lưu; raise báo lại lỗi. finally luôn gọi db.close() để đóng phiên làm việc.

db.add() đưa đối tượng vào phiên làm việc. db.flush() gửi dữ liệu xuống database
trong transaction hiện tại để lấy id và kiểm tra ràng buộc; dữ liệu đó vẫn rollback
được. db.commit() mới chốt transaction. Vì vậy không commit riêng từng bước seed.

Trong app/db/database.py:

- engine giữ cấu hình kết nối; SessionLocal tạo phiên làm việc.
- get_db mở phiên cho một request API; yield đưa phiên cho endpoint sử dụng,
  sau đó đóng ở finally; nếu có lỗi thì rollback.
- create_tables tạo các bảng còn thiếu từ model.
- update_soft_delete_schema kiểm tra và thêm deleted_at/index nếu DB cũ còn thiếu.
- check_tables dùng vòng lặp kiểm tra đủ bảng/cột.
- initialize_database gọi lần lượt ba bước trên; chỉ chạy khi gọi lệnh thủ công.

check_password_length nằm trong app/core/security.py và được dùng chung cho seed,
đăng ký và hash mật khẩu. Bcrypt giới hạn 72 byte nên vẫn cần encode('utf-8') để
kiểm tra đúng cả mật khẩu tiếng Việt. Mật khẩu không hợp lệ trả thông báo dễ hiểu.
Rollback bảo vệ thao tác dữ liệu seed/API. Với ALTER TABLE/CREATE INDEX, MySQL tự
commit DDL nên không thể dùng rollback để hoàn tác toàn bộ migration.
