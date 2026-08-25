# Worksheet

|TỔ CHỨC DỮ LIỆU — DATABASE SCHEMA GỢI Ý (STUDENT CLUB MANAGEMENT API)| | | | |
|---|---|---|---|---|
|Quan hệ chính: User 1–N Câu lạc bộ (owner); User N–N Câu lạc bộ qua ClubMember; Câu lạc bộ 1–N Hoạt động câu lạc bộ; User 1–N Hoạt động câu lạc bộ (assignee).| | | | |
| | | | | |
|Bảng|Trường|Kiểu dữ liệu|Ràng buộc|Ý nghĩa|
|users|id|INT / UUID|PK|Mã người dùng|
|users|email|VARCHAR|UNIQUE, NOT NULL|Email đăng nhập|
|users|password_hash|VARCHAR|NOT NULL|Mật khẩu đã hash|
|users|full_name|VARCHAR|NOT NULL|Họ tên|
|users|role|ENUM/VARCHAR|DEFAULT USER|USER / ADMIN|
|users|is_active|BOOLEAN|DEFAULT TRUE|Trạng thái tài khoản|
|users|created_at|DATETIME|NOT NULL|Ngày tạo|
|clubs|id|INT / UUID|PK|Mã câu lạc bộ|
|clubs|name|VARCHAR|NOT NULL|Tên câu lạc bộ|
|clubs|description|TEXT|NULL|Mô tả|
|clubs|owner_id|FK -> users.id|NOT NULL|Người sở hữu|
|clubs|created_at|DATETIME|NOT NULL|Ngày tạo|
|club_members|club_id|FK -> clubs.id|PK/UNIQUE pair|Câu lạc bộ|
|club_members|user_id|FK -> users.id|PK/UNIQUE pair|Thành viên|
|club_members|role|ENUM/VARCHAR|NOT NULL|OWNER / MEMBER|
|club_members|joined_at|DATETIME|NOT NULL|Ngày tham gia|
|club_activities|id|INT / UUID|PK|Mã hoạt động câu lạc bộ|
|club_activities|club_id|FK -> clubs.id|NOT NULL|Hoạt động câu lạc bộ thuộc câu lạc bộ|
|club_activities|title|VARCHAR|NOT NULL|Tiêu đề|
|club_activities|description|TEXT|NULL|Mô tả|
|club_activities|assignee_id|FK -> users.id|NULL|Người được giao|
|club_activities|status|ENUM/VARCHAR|NOT NULL|TODO / IN_PROGRESS / DONE|
|club_activities|priority|ENUM/VARCHAR|NOT NULL|LOW / MEDIUM / HIGH|
|club_activities|due_date|DATETIME|NULL|Hạn xử lý|
|club_activities|created_at|DATETIME|NOT NULL|Ngày tạo|
