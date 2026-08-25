# Worksheet

|ĐẶC TẢ API TỐI THIỂU — STUDENT CLUB MANAGEMENT API| | | | | | | |
|---|---|---|---|---|---|---|---|
| | | | | | | | |
|Module|Method|Endpoint|Auth|Quyền|Mục đích|Buổi|Mức độ|
|Auth|POST|/auth/register|Không|Public|Đăng ký tài khoản|2|Bắt buộc|
|Auth|POST|/auth/login|Không|Public|Đăng nhập và nhận JWT|2|Bắt buộc|
|Auth|POST|/auth/refresh|Refresh token|Public|Cấp lại access token|2|Bonus|
|User|GET|/users/me|JWT|User|Xem hồ sơ cá nhân|2|Bắt buộc|
|User|GET|/users|JWT|Admin|Danh sách/search người dùng|2|Bắt buộc|
|Câu lạc bộ|POST|/clubs|JWT|User|Tạo câu lạc bộ|3|Bắt buộc|
|Câu lạc bộ|GET|/clubs|JWT|User|Danh sách câu lạc bộ của tôi|3|Bắt buộc|
|Câu lạc bộ|GET|/clubs/{club_id}|JWT|Member|Chi tiết câu lạc bộ|3|Bắt buộc|
|Câu lạc bộ|PATCH|/clubs/{club_id}|JWT|Owner|Cập nhật câu lạc bộ|3|Bắt buộc|
|Câu lạc bộ|DELETE|/clubs/{club_id}|JWT|Owner|Xóa câu lạc bộ|3|Bắt buộc|
|Member|POST|/clubs/{club_id}/members|JWT|Owner|Thêm thành viên|3|Bắt buộc|
|Member|GET|/clubs/{club_id}/members|JWT|Member|Danh sách thành viên|3|Bắt buộc|
|Member|DELETE|/clubs/{club_id}/members/{user_id}|JWT|Owner|Xóa thành viên|3|Bắt buộc|
|Hoạt động câu lạc bộ|POST|/clubs/{club_id}/activities|JWT|Member|Tạo hoạt động câu lạc bộ|4|Bắt buộc|
|Hoạt động câu lạc bộ|GET|/clubs/{club_id}/activities|JWT|Member|List/filter/search hoạt động câu lạc bộ|4|Bắt buộc|
|Hoạt động câu lạc bộ|GET|/activities/{activity_id}|JWT|Member|Chi tiết hoạt động câu lạc bộ|4|Bắt buộc|
|Hoạt động câu lạc bộ|PATCH|/activities/{activity_id}|JWT|Theo permission|Cập nhật hoạt động câu lạc bộ|4|Bắt buộc|
|Hoạt động câu lạc bộ|DELETE|/activities/{activity_id}|JWT|Theo permission|Xóa hoạt động câu lạc bộ|4|Bắt buộc|
|Comment|POST|/activities/{activity_id}/comments|JWT|Member|Thêm comment|4|Bonus|
|Attachment|POST|/activities/{activity_id}/attachments|JWT|Member|Upload file|4|Bonus|
