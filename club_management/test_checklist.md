# Checklist Test API Quản Lý Câu Lạc Bộ (Tiết 4 & 5)

## I. Môi trường & Khởi tạo
- [ ] Database khởi tạo thành công (các bảng `users`, `clubs`, `club_members`, `club_activities`).
- [ ] Swagger hoạt động tại `http://localhost:8000/docs`.

## II. Xác thực & Người dùng (Auth & User)
- [ ] Đăng ký (`POST /auth/register`):
  - [ ] Case đúng: Tạo user thành công, password được băm (hash).
  - [ ] Case lỗi: Đăng ký với email đã tồn tại -> 400 Bad Request.
- [ ] Đăng nhập (`POST /auth/login`):
  - [ ] Case đúng: Đăng nhập thành công, trả về access token (JWT).
  - [ ] Case lỗi: Sai email hoặc password -> 400/401 Unauthorized.
- [ ] Hồ sơ cá nhân (`GET /users/me`):
  - [ ] Case đúng: Lấy đúng thông tin của mình khi có JWT.
  - [ ] Case lỗi: Không truyền JWT -> 401 Unauthorized.

## III. Quản lý Câu lạc bộ
- [ ] Tạo câu lạc bộ (`POST /clubs`):
  - [ ] Case đúng: User đăng nhập tạo câu lạc bộ thành công và tự động là OWNER.
- [ ] Danh sách câu lạc bộ của tôi (`GET /clubs`):
  - [ ] Case đúng: Trả về danh sách câu lạc bộ mà user là member/owner.
  - [ ] Case đúng: Tìm kiếm theo tên câu lạc bộ (`?search=...`).
- [ ] Thêm thành viên (`POST /clubs/{id}/members`):
  - [ ] Case đúng: OWNER thêm user khác vào câu lạc bộ thành công (role MEMBER).
  - [ ] Case lỗi: Người được thêm đã có trong câu lạc bộ -> 400.
  - [ ] Case lỗi: Người thêm không phải OWNER -> 403 Forbidden.

## IV. Hoạt động câu lạc bộ (Tiết 4)
- [ ] Tạo hoạt động (`POST /clubs/{id}/activities`):
  - [ ] Case đúng: Thành viên tạo hoạt động thành công.
  - [ ] Case lỗi: Gán `assignee_id` cho một người không thuộc câu lạc bộ -> 400 Bad Request.
  - [ ] Case lỗi: Người tạo không thuộc câu lạc bộ -> 403 Forbidden.
- [ ] Danh sách hoạt động (`GET /clubs/{id}/activities`):
  - [ ] Case đúng: Hiển thị đúng hoạt động của câu lạc bộ, phân trang đúng.
  - [ ] Case đúng: Lọc theo status, priority, và tìm kiếm theo tên thành công.
- [ ] Chi tiết hoạt động (`GET /activities/{id}`):
  - [ ] Case đúng: Xem chi tiết thành công nếu thuộc câu lạc bộ.
  - [ ] Case lỗi: Xem hoạt động của câu lạc bộ khác -> 403 Forbidden.
- [ ] Cập nhật hoạt động (`PATCH /activities/{id}`):
  - [ ] Case đúng: Cập nhật status/priority (chỉ gửi trường cần update).
  - [ ] Case lỗi: Không phải OWNER hoặc Assignee cập nhật -> 403 Forbidden.
- [ ] Xóa hoạt động (`DELETE /activities/{id}`):
  - [ ] Case đúng: OWNER xóa hoạt động thành công.
  - [ ] Case lỗi: MEMBER bình thường xóa -> 403 Forbidden.

## V. Swagger & Integration (Tiết 5)
- [ ] Các Endpoint đều có Summary và Description rõ ràng.
- [ ] Model dữ liệu (Schema) Response trả về khớp với tài liệu (không chứa `password_hash`).
- [ ] 100% case nghiệp vụ ở trên trả về Status Code đúng chuẩn (200, 201, 400, 403, 404), KHÔNG bị văng lỗi 500.

