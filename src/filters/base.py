from abc import ABC, abstractmethod
from typing import Dict, Type
import numpy as np

from ..exceptions import FilterError


class BaseFilter(ABC):
    """Абстрактный базовый класс для фильтров изображений"""

    def __init__(self, intensity: float = 1.0):
        self.intensity = max(0.0, min(1.0, intensity))

    @abstractmethod
    def apply(self, frame: np.ndarray) -> np.ndarray:
        """Применение фильтра к кадру"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Имя фильтра"""
        pass


class NoneFilter(BaseFilter):
    """None фильтр"""

    def apply(self, frame: np.ndarray) -> np.ndarray:
        return frame.copy()

    @property
    def name(self) -> str:
        return "none"


class FilterFactory:
    """Для создания экземпляров фильтров"""

    _filters: Dict[str, Type[BaseFilter]] = {}

    @classmethod
    def register(cls, filter_class: Type[BaseFilter]) -> None:
        """Регистрирует класс фильтра"""
        instance = filter_class()
        cls._filters[instance.name] = filter_class

    @classmethod
    def create(
        cls,
        filter_name: str,
        intensity: float = 1.0
    ) -> BaseFilter:
        """Создает экземпляр фильтра по имени"""
        if filter_name not in cls._filters:
            raise FilterError(f"Unknown filter: {filter_name}")

        return cls._filters[filter_name](intensity)

    @classmethod
    def get_available_filters(cls) -> list:
        """Возврат списока имен доступных фильтров"""
        return list(cls._filters.keys())


# Регистрация фильтра "none"
FilterFactory.register(NoneFilter)
