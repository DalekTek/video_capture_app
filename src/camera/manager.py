import threading
from queue import Queue
from typing import Optional
from loguru import logger

from ..config import Config
from ..exceptions import CameraError
from ..camera.capture import CameraCapture


class CameraManager:
    """Управляет операциями захвата изображенияя с камеры"""

    def __init__(self, config: Config):
        self.config = config
        self.capture = CameraCapture(config)
        self.capture_thread: Optional[threading.Thread] = None

    def start_capture(self, shutdown_event: threading.Event) -> None:
        """Запуск процесса захвата"""
        try:
            self.capture.initialize()
            self.capture.start_capture(shutdown_event)

        except CameraError as e:
            logger.error(f"Camera manager error: {e}")
            raise

    def stop_capture(self) -> None:
        """Останавка процесса захвата"""
        logger.info("Stopping camera capture")
        self.capture.stop_capture()

    def get_frame_queue(self) -> Queue:
        """Получение очереди кадров от объекта захвата"""
        return self.capture.get_frame_queue()