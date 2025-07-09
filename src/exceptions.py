class ApplicationError(Exception):
    """Базовое исключение"""
    pass


class ConfigurationError(ApplicationError):
    """Исключение при ошибках конфигурации"""
    pass


class CameraError(ApplicationError):
    """Исключение при ошибках камеры"""
    pass


class FilterError(ApplicationError):
    """Исключение при ошибках фильтров"""
    pass


class DisplayError(ApplicationError):
    """Исключение при ошибках отображения"""
    pass