import cv2
import numpy as np

from .base import BaseFilter, FilterFactory


class SharpenFilter(BaseFilter):
    """Фильтр повышения резкости"""

    def apply(self, frame: np.ndarray) -> np.ndarray:
        """Применяем фильтр повышения резкости"""
        # Базовая квадратная матрица для повышения резкости
        base_kernel = np.array([
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0]
        ], dtype=np.float32)

        # Единичная квадратная матрица (ядро)
        identity_kernel = np.array([
            [0, 0, 0],
            [0, 1, 0],
            [0, 0, 0]
        ], dtype=np.float32)

        # Интерполяция между единичным и ядром резкости на основе интенсивности
        kernel = identity_kernel * (1.0 - self.intensity) + base_kernel * self.intensity

        sharpened = cv2.filter2D(frame, -1, kernel)
        # Ограничиваем значения пикселей в диапазоне [0, 255]
        return np.clip(sharpened, 0, 255).astype(np.uint8)

    @property
    def name(self) -> str:
        return "sharpen"


FilterFactory.register(SharpenFilter)