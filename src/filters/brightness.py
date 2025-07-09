import cv2
import numpy as np

from .base import BaseFilter, FilterFactory


class BrightnessFilter(BaseFilter):
    """Фильтр повышения резкости для усиления краев"""

    def apply(self, frame: np.ndarray) -> np.ndarray:
        """Применяет регулировку яркости"""
        # Преобразование интенсивности (0.0-1.0) в регулировку яркости (от -100 до +100)
        brightness = (self.intensity - 0.5) * 200

        # Применение регулировки яркости с помощью convertScaleAbs для скорости
        adjusted = cv2.convertScaleAbs(frame, alpha=1.0, beta=brightness)
        return adjusted

    @property
    def name(self) -> str:
        return "brightness"


FilterFactory.register(BrightnessFilter)