import base64
import logging
from typing import List, Optional

import cv2
import insightface
import numpy as np

from app.core.config import settings

# Cấu hình Logger để ghi log ra màn hình console
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIEngine:
    """
    Core xử lý AI sử dụng thư viện InsightFace.
    Áp dụng Singleton pattern để chỉ load model một lần duy nhất khi khởi chạy.
    """

    def __init__(self):
        logger.info(f"Đang khởi tạo AI Engine với model: {settings.INSIGHTFACE_MODEL_NAME}")
        try:
            # Khởi tạo FaceAnalysis
            # Providers: Dùng 'CUDAExecutionProvider' nếu có GPU, 'CPUExecutionProvider' cho CPU.
            self.model = insightface.app.FaceAnalysis(
                name=settings.INSIGHTFACE_MODEL_NAME,
                root=str(settings.MODEL_DIR),
                providers=['CPUExecutionProvider']
            )
            # Chuẩn bị model (ctx_id=0 thường dùng cho GPU index 0, det_size là kích thước ảnh đầu vào)
            self.model.prepare(ctx_id=0, det_size=(640, 640))
            logger.info("AI Engine đã khởi động thành công.")
        except Exception as e:
            logger.critical(f"Lỗi nghiêm trọng: Không thể load model AI. {str(e)}")
            raise RuntimeError("Khởi tạo Model thất bại.") from e

    def _base64_to_image(self, base64_string: str) -> Optional[np.ndarray]:
        """
        Chuyển đổi chuỗi Base64 thành ảnh OpenCV (numpy array).
        """
        try:
            # Loại bỏ phần header nếu có (ví dụ: "data:image/jpeg;base64,...")
            if "," in base64_string:
                base64_string = base64_string.split(",")[1]

            image_data = base64.b64decode(base64_string)
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return img
        except Exception as e:
            logger.error(f"Lỗi khi decode Base64: {str(e)}")
            return None

    def get_embedding(self, image_base64: str) -> Optional[List[float]]:
        """
        Trích xuất vector đặc trưng (Embedding) từ 1 ảnh.
        Kết quả trả về là vector 512 chiều của khuôn mặt lớn nhất tìm thấy.
        """
        img = self._base64_to_image(image_base64)
        if img is None:
            return None

        # Đưa ảnh vào model để detect
        faces = self.model.get(img)
        if not faces:
            return None

        # Thuật toán heuristic: Chọn khuôn mặt có diện tích lớn nhất (Bounding Box area)
        # để tránh lấy nhầm người đi đường hoặc nhiễu ở background.
        main_face = max(faces, key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]))

        # Trả về embedding dưới dạng List (thay vì numpy array) để tương thích JSON
        return main_face.embedding.tolist()

    def get_average_embedding(self, images: List[str]) -> Optional[List[float]]:
        """
        Tính toán vector trung bình từ danh sách nhiều ảnh.
        Dùng trong quá trình Đăng ký để tạo ra một vector mẫu (reference) chính xác hơn.
        """
        vectors = []
        for img_b64 in images:
            vec = self.get_embedding(img_b64)
            if vec:
                vectors.append(vec)

        if not vectors:
            return None

        # Tính trung bình cộng (Mean Pooling) dọc theo các chiều của vector
        avg_vector = np.mean(vectors, axis=0)

        # Chuẩn hóa L2 (Normalization): Bước cực kỳ quan trọng.
        # Đảm bảo vector có độ dài bằng 1 để tính Cosine Similarity chính xác.
        norm_val = np.linalg.norm(avg_vector)
        if norm_val > 0:
            avg_vector = avg_vector / norm_val

        return avg_vector.tolist()

    @staticmethod
    def compute_similarity(embed1: List[float], embed2: List[float]) -> float:
        """
        Tính độ tương đồng Cosine giữa 2 vector.
        Kết quả từ -1 đến 1 (càng gần 1 càng giống nhau).
        """
        if not embed1 or not embed2:
            return 0.0

        v1 = np.array(embed1)
        v2 = np.array(embed2)

        # Tính toán lại chuẩn (norm) để đảm bảo an toàn số học
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)

        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0

        return float(np.dot(v1, v2) / (norm_v1 * norm_v2))


# Khởi tạo instance duy nhất (Singleton)
ai_service = AIEngine()
