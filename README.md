# Face Auth API (Backend)

## Mục lục

* [Giới thiệu](#giới-thiệu)
* [Kiến trúc Backend](#kiến-trúc-backend)
* [Công nghệ sử dụng](#công-nghệ-sử-dụng)
* [Luồng xử lý xác thực](#luồng-xử-lý-xác-thực)
* [Cấu trúc thư mục](#cấu-trúc-thư-mục)
* [Cài đặt & Chạy dự án](#cài-đặt--chạy-dự-án)
* [Cấu hình hệ thống](#cấu-hình-hệ-thống)
* [API Endpoints](#api-endpoints)
* [Hạn chế & Lưu ý](#hạn-chế--lưu-ý)
* [Hướng phát triển](#hướng-phát-triển)

---

## Giới thiệu

**Face Auth API** là backend cung cấp dịch vụ xác thực người dùng bằng **mật khẩu kết hợp nhận diện khuôn mặt**. Hệ thống sử dụng mô hình **InsightFace** để trích xuất embedding khuôn mặt và so khớp bằng **Cosine Similarity**.

Backend được thiết kế theo kiến trúc **FastAPI + Service Layer**, dễ đọc, dễ mở rộng và phù hợp cho các dự án học tập hoặc demo xác thực sinh trắc học.

---

## Kiến trúc Backend

```
Client (Frontend)
   ↓ REST API
FastAPI Router
   ↓
Service Layer
 ├─ AI Engine (Face Embedding)
 └─ User Service (CRUD User)
   ↓
JSON Storage (users.json)
```

---

## Công nghệ sử dụng

* Python 3.x
* FastAPI
* InsightFace (buffalo_l / buffalo_s)
* OpenCV
* NumPy
* Pydantic
* Uvicorn

---

## Luồng xử lý xác thực

### Đăng ký

1. Nhận username, password và danh sách ảnh Base64
2. Trích xuất embedding cho từng ảnh
3. Tính **vector trung bình** và chuẩn hóa
4. Lưu thông tin user vào file JSON

### Đăng nhập

1. Kiểm tra username và password
2. Trích xuất embedding từ ảnh hiện tại
3. So khớp với vector đã lưu
4. So sánh với ngưỡng cấu hình

---

## Cấu trúc thư mục

```
Backend/
├── app/
│   ├── core/        # Config hệ thống
│   ├── routers/     # API routes
│   ├── schemas/     # Pydantic schemas
│   ├── services/    # AI Engine, User Service
│   └── main.py      # Entry point
│
├── data/            # users.json
├── models/          # InsightFace models
└── requirements.txt
```

---

## Cài đặt & Chạy dự án

```bash
cd Backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Truy cập API docs:

```
http://localhost:8000/docs
```

---

## Cấu hình hệ thống

File cấu hình chính:

```
app/core/config.py
```

Thông số quan trọng:

* `INSIGHTFACE_MODEL_NAME`: buffalo_l (chính xác cao) hoặc buffalo_s (nhẹ)
* `FACE_SIMILARITY_THRESHOLD`: ngưỡng xác thực (mặc định 0.65)
* `DB_FILE`: đường dẫn lưu dữ liệu user

---

## API Endpoints

### Register

```
POST /api/v1/auth/register
```

```json
{
  "username": "string",
  "password": "string",
  "images": ["base64_1", "base64_2", "..."]
}
```

### Login

```
POST /api/v1/auth/login
```

```json
{
  "username": "string",
  "password": "string",
  "image_base64": "base64_image"
}
```

---

## Hạn chế & Lưu ý

* Dữ liệu lưu bằng JSON, không phù hợp production
* Mật khẩu **chưa mã hóa**
* Chưa có JWT / session

---

## Hướng phát triển

* Hash mật khẩu (bcrypt)
* Thay JSON bằng Database (PostgreSQL, MongoDB)
* Thêm JWT Authentication
* Liveness Detection
* Docker hóa backend
