import cv2
import numpy as np

from .base import BaseFilter, FilterFactory


class BlurFilter(BaseFilter):
    """Фильтр размытия по Гауссу для уменьшения шума"""

    def apply(self, frame: np.ndarray) -> np.ndarray:
        """Размытие по Гауссу к кадру"""
        # Определяем размер квадратной матрицы (ядра, kernel) на основе интенсивности
        # В результате размер ядра плавно увеличивается от 5 до 15 по мере роста интенсивности,
        kernel_size = int(5 + self.intensity * 10)

        # Ядро обязательно должно быть нечетного размера (например, 5x5, 7x7, 9x9),
        # чтобы центр ядра совпадал с обрабатываемым пикселем
        if kernel_size % 2 == 0:
            kernel_size += 1

        return cv2.GaussianBlur(frame, (kernel_size, kernel_size), 0)

    @property
    def name(self) -> str:
        return "blur"


FilterFactory.register(BlurFilter)