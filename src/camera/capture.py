import threading
import time
from queue import Queue, Full
from typing import Optional

import cv2
from loguru import logger

from ..config import Config
from ..exceptions import CameraError


class CameraCapture:
    """Обрабатывает захват видео с камеры"""

    def __init__(self, config: Config):
        self.config = config
        self.camera: Optional[cv2.VideoCapture] = None
        self.frame_queue: Queue = Queue(maxsize=config.max_queue_size)
        self.capture_lock = threading.Lock() # Блокировка для потокобезопасного доступа к камере
        self.is_capturing = False

    def initialize(self) -> None:
        """Инициализирует захват с камеры"""
        try:
            self.camera = cv2.VideoCapture(self.config.camera_index)
            if not self.camera.isOpened():
                raise CameraError(f"Failed to open camera {self.config.camera_index}")

            # Установка свойств камеры (ширина, высота, FPS)
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.frame_width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.frame_height)
            self.camera.set(cv2.CAP_PROP_FPS, self.config.fps)

            logger.info(f"Camera initialized: {self.config.camera_index}")

        except Exception as e:
            raise CameraError(f"Failed to initialize camera: {e}")

    def start_capture(self, shutdown_event: threading.Event) -> None:
        """Запускает захват кадров в цикле"""
        if not self.camera:
            raise CameraError("Camera not initialized")

        self.is_capturing = True            # Флаг захвата кадров
        frame_time = 1.0 / self.config.fps  # Время между кадрами в секундах

        logger.info("Starting camera capture")

        try:
            # Цикл захвата кадров
            while not shutdown_event.is_set() and self.is_capturing:
                start_time = time.time()

                # Захват кадра с блокировкой для потокобезопасности
                with self.capture_lock:
                    ret, frame = self.camera.read()

                if not ret:  # Если кадр не был захвачен, пропускаем итерацию
                    logger.warning("Failed to read frame from camera")
                    continue

                # Добавление кадра в очередь
                try:
                    self.frame_queue.put(frame, block=False)
                except Full:
                    # Если очередь заполнена, удаляем самый старый кадр
                    try:
                        self.frame_queue.get_nowait()
                        self.frame_queue.put(frame, block=False)
                    except:
                        pass

                # Поддержание частоты кадров
                elapsed = time.time() - start_time
                # Вычисление времени ожидания для поддержания заданного FPS
                sleep_time = max(0, int(frame_time - elapsed))
                if sleep_time > 0:
                    time.sleep(sleep_time)

        except Exception as e:
            logger.error(f"Capture error: {e}")
            raise CameraError(f"Capture failed: {e}")
        finally:
            self.is_capturing = False
            logger.info("Camera capture stopped")

    def stop_capture(self) -> None:
        """Останавливает захват"""
        self.is_capturing = False

        if self.camera:
            # с блокировкой освобождаем ресурсы камеры
            with self.capture_lock:
                self.camera.release()
            logger.info("Camera released")

    def get_frame_queue(self) -> Queue:
        """Возвращает очередь кадров"""
        return self.frame_queue