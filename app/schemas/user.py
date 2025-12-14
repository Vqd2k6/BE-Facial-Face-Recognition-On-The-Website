from typing import Optional, List, Dict, Any

from pydantic import BaseModel


class LoginRequest(BaseModel):
    """Cấu trúc dữ liệu gửi lên để đăng nhập."""
    username: str
    password: str
    image_base64: str  # Chuỗi ảnh Base64 dùng để xác thực khuôn mặt


class RegisterRequest(BaseModel):
    """Cấu trúc dữ liệu gửi lên để đăng ký."""
    username: str
    password: str
    images: List[str]  # Danh sách các ảnh Base64 để model học khuôn mặt


class UserInDB(BaseModel):
    """Model User được lưu trong Database (file JSON)."""
    username: str
    password: str
    face_vector: List[float]  # Vector đặc trưng 512 chiều


class AuthResponse(BaseModel):
    """Cấu trúc phản hồi chuẩn (Response) trả về cho Client."""
    status: str
    message: str
    similarity: Optional[float] = None
    data: Optional[Dict[str, Any]] = None
