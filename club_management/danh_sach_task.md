# Danh sách task

|DANH SÁCH TASK — STUDENT CLUB MANAGEMENT API| | | | | | | | | | |
|---|---|---|---|---|---|---|---|---|---|---|
|Bảng phân rã công việc theo 5 buổi (tiết) học; mỗi task gắn với mức độ Bắt buộc/Không bắt buộc và điểm số tương ứng.| | | | | | | | | | |
| | | | | | | | | | | |
|Danh sách task|Chức năng|Chức năng chi tiết|Mức độ|Deadline| | | | |Điểm bắt buộc|Điểm Không bắt buộc|
| | | | |Tiết 1|Tiết 2|Tiết 3|Tiết 4|Tiết 5| | |
|Khởi tạo dự án|Cấu trúc source|Khởi tạo FastAPI project theo cấu trúc module: routers, models, schemas, services, dependencies, core, db.|Bắt buộc|Hoàn thiện| | | | |2| |
|Khởi tạo dự án|Cấu hình môi trường|Tạo .env/.env.example; cấu hình DATABASE_URL, SECRET_KEY, JWT settings và đọc config từ môi trường.|Bắt buộc|Hoàn thiện| | | | |2| |
|Database|Kết nối DB|Kết nối MySQL bằng SQLAlchemy; xây dựng engine, SessionLocal và dependency get_db.|Bắt buộc|Hoàn thiện| | | | |2| |
|Database|Thiết kế model|Tạo model User, Club, ClubMember, ClubActivity; khóa chính, khóa ngoại, timestamps và quan hệ phù hợp.|Bắt buộc|Hoàn thiện| | | | |3| |
|Database|Pydantic schema|Tạo Base/Create/Update/Response schema cho các entity chính; bật ORM/from_attributes khi cần.|Bắt buộc|Hoàn thiện| | | | |2| |
|Database|Khởi tạo bảng|Tạo bảng/migration ban đầu và kiểm tra DB khởi tạo thành công.|Bắt buộc|Hoàn thiện| | | | |2| |
|Core|Exception & response|Thiết lập exception cơ bản (404/400/403), format lỗi thống nhất và health-check endpoint.|Bắt buộc|Hoàn thiện| | | | |2| |
|Nâng cao|Seed dữ liệu|Viết script seed user/câu lạc bộ/hoạt động câu lạc bộ mẫu phục vụ test và demo.|Không bắt buộc|Hoàn thiện| | | | | |5|
|Authentication|Register|POST /auth/register: tạo tài khoản, kiểm tra email trùng, validate dữ liệu đầu vào.|Bắt buộc| |Hoàn thiện| | | |2| |
|Authentication|Password|Hash mật khẩu bằng bcrypt/passlib; tuyệt đối không lưu mật khẩu dạng plain text.|Bắt buộc| |Hoàn thiện| | | |2| |
|Authentication|Login|POST /auth/login: xác thực email/password và trả access token JWT hợp lệ.|Bắt buộc| |Hoàn thiện| | | |3| |
|Authentication|Current user|Xây dựng OAuth2PasswordBearer + dependency get_current_user để đọc user từ JWT.|Bắt buộc| |Hoàn thiện| | | |2| |
|Authorization|Role guard|Phân quyền cơ bản USER/ADMIN hoặc dependency kiểm tra role cho endpoint quản trị.|Bắt buộc| |Hoàn thiện| | | |2| |
|User|Profile|GET /users/me: trả thông tin người dùng hiện tại, không lộ password_hash.|Bắt buộc| |Hoàn thiện| | | |2| |
|User|Danh sách user|GET /users: chỉ Admin; có search theo tên/email và trạng thái.|Bắt buộc| |Hoàn thiện| | | |2| |
|Validation|Lỗi nghiệp vụ|Xử lý lỗi token hết hạn/sai, đăng nhập sai, tài khoản không hoạt động bằng HTTP status phù hợp.|Bắt buộc| |Hoàn thiện| | | |2| |
|Nâng cao|Refresh token|Bổ sung refresh token và endpoint cấp lại access token.|Không bắt buộc| |Hoàn thiện| | | | |5|
|Nâng cao|Rate limit|Giới hạn tần suất gọi login hoặc cơ chế chống brute-force ở mức demo.|Không bắt buộc| |Hoàn thiện| | | | |5|
|Câu lạc bộ|Tạo câu lạc bộ|POST /clubs: user đăng nhập tạo câu lạc bộ và tự động trở thành OWNER.|Bắt buộc| | |Hoàn thiện| | |2| |
|Câu lạc bộ|Danh sách câu lạc bộ|GET /clubs: chỉ trả câu lạc bộ mà user là owner/member; hỗ trợ search tên câu lạc bộ.|Bắt buộc| | |Hoàn thiện| | |2| |
|Câu lạc bộ|Chi tiết câu lạc bộ|GET /clubs/{id}: chỉ thành viên câu lạc bộ mới được xem.|Bắt buộc| | |Hoàn thiện| | |2| |
|Câu lạc bộ|Cập nhật/xóa|PUT/PATCH/DELETE câu lạc bộ; chỉ OWNER được sửa/xóa.|Bắt buộc| | |Hoàn thiện| | |2| |
|Câu lạc bộ member|Thêm thành viên|POST /clubs/{id}/members: owner thêm user vào câu lạc bộ; không cho thêm trùng.|Bắt buộc| | |Hoàn thiện| | |2| |
|Câu lạc bộ member|Xóa thành viên|DELETE /clubs/{id}/members/{user_id}: owner xóa member; không được xóa owner cuối cùng.|Bắt buộc| | |Hoàn thiện| | |2| |
|Câu lạc bộ member|Danh sách thành viên|GET /clubs/{id}/members: trả danh sách member và role trong câu lạc bộ.|Bắt buộc| | |Hoàn thiện| | |1| |
|Validation|Dữ liệu Câu lạc bộ|Tên câu lạc bộ không trống, không vượt giới hạn; xử lý câu lạc bộ/user không tồn tại.|Bắt buộc| | |Hoàn thiện| | |1| |
|Nâng cao|Activity log|Lưu lịch sử thao tác quan trọng: tạo/sửa câu lạc bộ, thêm/xóa member.|Không bắt buộc| | |Hoàn thiện| | | |5|
|Nâng cao|Soft delete|Câu lạc bộ có deleted_at/is_deleted và không mất dữ liệu khi xóa.|Không bắt buộc| | |Hoàn thiện| | | |5|
|Hoạt động câu lạc bộ|Tạo hoạt động câu lạc bộ|POST /clubs/{id}/activities: thành viên có quyền tạo hoạt động câu lạc bộ với title, description, due_date, priority.|Bắt buộc| | | |Hoàn thiện| |2| |
|Hoạt động câu lạc bộ|Danh sách hoạt động câu lạc bộ|GET /clubs/{id}/activities: trả hoạt động câu lạc bộ thuộc câu lạc bộ, không lộ hoạt động câu lạc bộ câu lạc bộ khác.|Bắt buộc| | | |Hoàn thiện| |1| |
|Hoạt động câu lạc bộ|Chi tiết hoạt động câu lạc bộ|GET /activities/{id}: kiểm tra user thuộc câu lạc bộ trước khi trả dữ liệu.|Bắt buộc| | | |Hoàn thiện| |1| |
|Hoạt động câu lạc bộ|Cập nhật hoạt động câu lạc bộ|PATCH /activities/{id}: cập nhật các trường hợp lệ, không ghi đè trường không gửi lên.|Bắt buộc| | | |Hoàn thiện| |2| |
|Hoạt động câu lạc bộ|Xóa hoạt động câu lạc bộ|DELETE /activities/{id}: áp dụng permission phù hợp và trả response đúng chuẩn.|Bắt buộc| | | |Hoàn thiện| |1| |
|Hoạt động câu lạc bộ|Giao việc|Gán assignee là một thành viên đang sinh hoạt trong câu lạc bộ; không cho gán user ngoài câu lạc bộ.|Bắt buộc| | | |Hoàn thiện| |2| |
|Hoạt động câu lạc bộ|Workflow|Quản lý status TODO/IN_PROGRESS/DONE và priority LOW/MEDIUM/HIGH với validation.|Bắt buộc| | | |Hoàn thiện| |1| |
|Hoạt động câu lạc bộ|Search & filter|Filter theo status, priority, assignee; search title; có thể kết hợp nhiều điều kiện.|Bắt buộc| | | |Hoàn thiện| |2| |
|Hoạt động câu lạc bộ|Pagination & sort|Phân trang limit/offset hoặc page/size; sort theo created_at/due_date.|Bắt buộc| | | |Hoàn thiện| |1| |
|Authorization|Permission matrix|Owner/member/assignee có quyền khác nhau; endpoint phải chặn truy cập trái phép bằng 403.|Bắt buộc| | | |Hoàn thiện| |2| |
|Nâng cao|Comment|Thêm comment (trao đổi trong ban chủ nhiệm/ban tổ chức) cho hoạt động câu lạc bộ; chỉ thành viên câu lạc bộ được xem/tạo comment.|Không bắt buộc| | | |Hoàn thiện| | |5|
|Nâng cao|Attachment|Upload file đính kèm (minh chứng, hình ảnh hoạt động phong trào) cho hoạt động câu lạc bộ, kiểm tra loại/kích thước file và lưu đường dẫn.|Không bắt buộc| | | |Hoàn thiện| | |5|
|Quality|Test API|Lập checklist test luồng chính trên Swagger/Postman; test cả case đúng và case lỗi.|Bắt buộc| | | | |Hoàn thiện|2| |
|Quality|Fix bug|Sửa lỗi phát hiện khi integration test; không còn lỗi 500 ở các case nghiệp vụ thông thường.|Bắt buộc| | | | |Hoàn thiện|1| |
|Documentation|Swagger|Hoàn thiện summary/description, response model, status code và tags để Swagger dễ đọc.|Bắt buộc| | | | |Hoàn thiện|1| |
|TỔNG ĐIỂM| | | | | | | | |65|35|
