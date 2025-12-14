import json
import logging
from typing import Dict, Optional

from app.core.config import settings
from app.schemas.user import UserInDB

logger = logging.getLogger(__name__)


class UserService:
    """
    Quản lý việc lưu trữ dữ liệu User và Cache trong RAM.
    Sử dụng file JSON làm nơi lưu trữ (Database đơn giản).
    """

    def __init__(self):
        self.db_path = settings.DB_FILE
        # Cache trong RAM: Sử dụng Dictionary (Hash Map) để tìm kiếm cực nhanh O(1)
        self.users_cache: Dict[str, UserInDB] = {}
        self._load_db()

    def _load_db(self):
        """Đọc dữ liệu từ file JSON vào RAM ngay khi khởi động."""
        if not self.db_path.exists():
            # Nếu chưa có file db, tạo thư mục và file rỗng
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump([], f)
            return

        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Convert danh sách từ JSON sang Dictionary Pydantic Object
                self.users_cache = {u["username"]: UserInDB(**u) for u in data}
            logger.info(f"Dịch vụ đã khởi tạo. Đã load {len(self.users_cache)} users.")
        except Exception as e:
            logger.error(f"Lỗi Persistence: Không thể đọc database. {e}")
            self.users_cache = {}

    def _save_db(self):
        """Ghi đè dữ liệu từ RAM xuống đĩa cứng (Persistence)."""
        try:
            data = [u.model_dump() for u in self.users_cache.values()]
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"Lỗi Persistence: Không thể lưu database. {e}")

    def get_user_by_username(self, username: str) -> Optional[UserInDB]:
        """Tìm user trong Cache (Tốc độ tức thì)."""
        return self.users_cache.get(username)

    def create_user(self, user_data: UserInDB):
        """Thêm user mới vào Cache và kích hoạt lưu xuống file."""
        self.users_cache[user_data.username] = user_data
        self._save_db()
        logger.info(f"Đã đăng ký user mới: {user_data.username}")


# Khởi tạo instance duy nhất
user_service = UserService()
