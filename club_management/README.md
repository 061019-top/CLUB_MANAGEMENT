# Student Club Management API

## Cài đặt và Chạy

1. Tạo môi trường ảo và cài đặt thư viện:
```bash
pip install -r requirements.txt
```

2. Đổi tên `.env.example` thành `.env` và cập nhật thông tin DATABASE_URL

3. Chạy script seed data:
```bash
python seed.py
```

4. Chạy server FastAPI:
```bash
uvicorn app.main:app --reload
```
