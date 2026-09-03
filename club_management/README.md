# Student Club Management API

## Cài đặt và chạy bằng PowerShell

Mở PowerShell tại thư mục `CLUB_MANAGEMENT`, sau đó di chuyển vào thư mục dự án:

```powershell
Set-Location .\club_management
```

1. Tạo môi trường ảo:

```powershell
python -m venv venv
```

2. Kích hoạt môi trường ảo:

```powershell
.\venv\Scripts\Activate.ps1
```

Nếu PowerShell chặn script kích hoạt, chạy:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

3. Cài đặt các thư viện:

```powershell
python -m pip install -r requirements.txt
```

4. Tạo file `.env` từ file mẫu:

```powershell
Copy-Item .env.example .env
```

Nếu `.env` đã tồn tại thì bỏ qua lệnh trên. Mở `.env` và cập nhật `DATABASE_URL`, `SECRET_KEY` cùng các cấu hình cần thiết.

5. Chạy server FastAPI:

```powershell
python -m uvicorn app.main:app --reload
```

Sau khi server khởi động, truy cập:

- Swagger UI: <http://127.0.0.1:8000/docs>
- Health check: <http://127.0.0.1:8000/health>

## Cấu hình môi trường

- `.env` chứa cấu hình thật trên máy cá nhân và không được commit lên Git.
- `.env.example` là file mẫu không chứa mật khẩu hoặc secret thật và nên được commit.
