import logging

from fastapi import APIRouter, HTTPException, status

from app.core.config import settings
from app.schemas.user import RegisterRequest, LoginRequest, AuthResponse, UserInDB
from app.services.ai_engine import ai_service
from app.services.user_service import user_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """
    Xử lý luồng Đăng ký (Register Flow).
    Các bước thực hiện:
    1. Validate dữ liệu đầu vào.
    2. Kiểm tra user đã tồn tại chưa.
    3. Dùng AI tính vector trung bình từ các ảnh upload.
    4. Lưu thông tin user và vector vào DB.
    """
    # 1. Kiểm tra đầu vào
    if not request.images:
        raise HTTPException(status_code=400, detail="Không có ảnh nào được gửi lên.")

    # 2. Kiểm tra trùng lặp
    if user_service.get_user_by_username(request.username):
        raise HTTPException(status_code=400, detail="Tên đăng nhập đã tồn tại.")

    # 3. Trích xuất đặc trưng khuôn mặt (AI)
    logger.info(f"Bắt đầu xử lý đăng ký cho user: {request.username}")
    avg_vector = ai_service.get_average_embedding(request.images)

    if not avg_vector:
        raise HTTPException(status_code=400, detail="Không tìm thấy khuôn mặt rõ ràng trong ảnh.")

    # 4. Lưu dữ liệu
    # Lưu ý: Mật khẩu hiện tại chưa được mã hóa (Cần nâng cấp bảo mật sau này)
    new_user = UserInDB(
        username=request.username,
        password=request.password,
        face_vector=avg_vector
    )
    user_service.create_user(new_user)

    return AuthResponse(
        status="success",
        message="Đăng ký tài khoản thành công."
    )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """
    Xử lý luồng Đăng nhập (Authentication Flow).
    Các bước thực hiện:
    1. Tìm user trong DB.
    2. Kiểm tra mật khẩu (Password Matching).
    3. Kiểm tra khuôn mặt (Face Verification).
    """
    # 1. Tìm User
    user = user_service.get_user_by_username(request.username)
    if not user:
        raise HTTPException(status_code=404, detail="Tài khoản không tồn tại.")

    # 2. Xác thực mật khẩu
    if user.password != request.password:
        raise HTTPException(status_code=401, detail="Sai mật khẩu.")

    # 3. Xác thực sinh trắc học
    current_vector = ai_service.get_embedding(request.image_base64)
    if not current_vector:
        raise HTTPException(status_code=400, detail="Không phát hiện khuôn mặt trong ảnh gửi lên.")

    # Tính điểm tương đồng
    similarity = ai_service.compute_similarity(user.face_vector, current_vector)
    logger.info(f"Thử đăng nhập - User: {request.username} | Điểm số: {similarity:.4f}")

    if similarity > settings.FACE_SIMILARITY_THRESHOLD:
        return AuthResponse(
            status="success",
            message="Đăng nhập thành công.",
            similarity=similarity
        )

    # Trả về 401 nếu mặt không khớp
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Xác thực khuôn mặt thất bại. Độ khớp: {similarity:.2f}"
    )
