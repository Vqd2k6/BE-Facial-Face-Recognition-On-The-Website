from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Cấu hình toàn cục cho ứng dụng.
    Tự động load biến môi trường hoặc dùng giá trị mặc định.
    """
    PROJECT_NAME: str = "Face Auth API"
    API_V1_STR: str = "/api/v1"

    # Định vị đường dẫn gốc của dự án (Project Root)
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

    # Đường dẫn lưu Data và Model
    DB_FILE: Path = BASE_DIR / "data" / "users.json"
    MODEL_DIR: Path = BASE_DIR / "models"

    # Cấu hình Model AI
    # 'buffalo_l': Độ chính xác cao hơn (ResNet50), tốc độ chậm hơn.
    # 'buffalo_s': Tốc độ nhanh (MobileNet), độ chính xác thấp hơn.
    INSIGHTFACE_MODEL_NAME: str = "buffalo_l"

    # Ngưỡng so sánh (Similarity Threshold)
    # 0.65 là mức khuyến nghị cho model buffalo_l để cân bằng giữa
    # việc nhận diện sai (False Positive) và bỏ sót (False Negative).
    FACE_SIMILARITY_THRESHOLD: float = 0.65

    class Config:
        case_sensitive = True


settings = Settings()
