import os
from dataclasses import dataclass
import importlib
from pathlib import Path

from .exceptions import ConfigurationError


@dataclass
class Config:
    """Configuration class for video capture application."""

    # Настройки камеры
    camera_index: int
    frame_width: int
    frame_height: int
    fps: int

    # Настройки отображения
    window_title: str
    display_scale: float

    # Настройки фильтров
    default_filter: str
    filter_intensity: float

    # Настройки производительности
    max_queue_size: int
    capture_timeout: float

    # Настройки логирования
    log_level: str

    def __init__(self):
        try:
            self.camera_index = self._get_int_env("CAMERA_INDEX", 0)
            self.frame_width = self._get_int_env("FRAME_WIDTH", 640)
            self.frame_height = self._get_int_env("FRAME_HEIGHT", 480)
            self.fps = self._get_int_env("FPS", 30)

            self.window_title = self._get_str_env("WINDOW_TITLE", "Video Capture")
            self.display_scale = self._get_float_env("DISPLAY_SCALE", 1.0)

            self.default_filter = self._get_str_env("DEFAULT_FILTER", "none")
            self.filter_intensity = self._get_float_env("FILTER_INTENSITY", 1.0)
            self.list_available_filters = self._get_list_env("AVAILABLE_FILTERS", ["none"])
            self.register_available_filters()

            self.max_queue_size = self._get_int_env("MAX_QUEUE_SIZE", 10)
            self.capture_timeout = self._get_float_env("CAPTURE_TIMEOUT", 5.0)

            self.log_level = self._get_str_env("LOG_LEVEL", "DEBUG")

            self._validate_config()

        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {e}")

    def _get_str_env(self, key: str, default: str) -> str:
        """Получить строковую переменную окружения со значением по умолчанию"""
        return os.getenv(key, default)

    def _get_list_env(self, key: str, default: list) -> list:
        """Получить список из переменной окружения, разделенной запятыми"""
        value = os.getenv(key)
        if value is None:
            return default
        return [item.strip() for item in value.split(",") if item.strip()]

    def _get_int_env(self, key: str, default: int) -> int:
        """Получить целочисленную переменную окружения со значением по умолчанию"""
        value = os.getenv(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            raise ConfigurationError(f"Invalid integer value for {key}: {value}")

    def _get_float_env(self, key: str, default: float) -> float:
        """Получить float переменную окружения со значением по умолчанию"""
        value = os.getenv(key)
        if value is None:
            return default
        try:
            return float(value)
        except ValueError:
            raise ConfigurationError(f"Invalid float value for {key}: {value}")

    def register_available_filters(self):
        filters_dir = Path(__file__).parent / "filters"
        for filter_name in self.list_available_filters:
            if filter_name == "none":
                continue  # NoneFilter уже зарегистрирован
            filter_file = filters_dir / f"{filter_name}.py"
            if not filter_file.exists():
                raise ConfigurationError(f"Filter file not found: {filter_file}")
            try:
                module = importlib.import_module(f"src.filters.{filter_name}")
                # Имя класса фильтра по соглашению: BlurFilter, SharpenFilter и т.д.
                class_name = f"{filter_name.capitalize()}Filter"
                filter_class = getattr(module, class_name)
                from .filters.base import FilterFactory
                FilterFactory.register(filter_class)
            except Exception as e:
                raise ConfigurationError(f"Failed to register filter '{filter_name}': {e}")

    def _validate_config(self) -> None:
        """Проверка корректности конфигурации"""
        if self.camera_index < 0:
            raise ConfigurationError("Camera index must be non-negative")

        if self.frame_width <= 0 or self.frame_height <= 0:
            raise ConfigurationError("Frame dimensions must be positive")

        if self.fps <= 0:
            raise ConfigurationError("FPS must be positive")

        if self.display_scale <= 0:
            raise ConfigurationError("Display scale must be positive")

        if self.filter_intensity < 0:
            raise ConfigurationError("Filter intensity must be non-negative")

        if self.max_queue_size <= 0:
            raise ConfigurationError("Max queue size must be positive")

        if self.capture_timeout <= 0:
            raise ConfigurationError("Capture timeout must be positive")

        valid_filters = ["none", "blur", "sharpen", "brightness"]
        if self.default_filter not in valid_filters:
            raise ConfigurationError(f"Invalid filter: {self.default_filter}")
