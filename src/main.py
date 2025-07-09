import signal
import sys
import threading
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from loguru import logger

from .config import Config
from .camera.manager import CameraManager
from .display.window import DisplayWindow
from .exceptions import ApplicationError, ConfigurationError


class VideoApplication:
    """Класс работы с видео (захват и обработка)"""

    def __init__(self):
        self.config: Optional[Config] = None
        self.camera_manager: Optional[CameraManager] = None
        self.display_window: Optional[DisplayWindow] = None
        self.running = False
        self._shutdown_event = threading.Event() # Событие для завершения потоков
        # Используется для синхронизации завершения работы между потоками:
        # если вызвать self._shutdown_event.set(), все потоки, которые проверяют shutdown_event.is_set(),
        # узнают, что нужно завершаться.

    def initialize(self) -> None:
        """Инициалиация с настройками"""
        try:
            self.config = Config()
            logger.info("Configuration loaded successfully")

            self.camera_manager = CameraManager(self.config)
            self.display_window = DisplayWindow(self.config)

            # Настройка обработчиков сигналов для корректного завершения
            # Функция _signal_handler будет вызвана при получении сигналов SIGINT и SIGTERM
            signal.signal(signal.SIGINT, self._signal_handler) # Обрабатывает сигнал прерывания (Ctrl+C)
            signal.signal(signal.SIGTERM, self._signal_handler) # Обрабатывает сигнал завершения (kill)

            logger.info("Application initialized successfully")

        except ConfigurationError as e:
            logger.error(f"Configuration error: {e}")
            raise
        except Exception as e:
            logger.error(f"Initialization error: {e}")
            raise ApplicationError(f"Failed to initialize application: {e}")

    def run(self) -> None:
        if not self.config or not self.camera_manager or not self.display_window:
            raise ApplicationError("Application not properly initialized")

        try:
            logger.info("Starting video capture application")
            self.running = True

            # Запуск захвата с камеры в отдельном потоке
            camera_thread = threading.Thread(
                target=self.camera_manager.start_capture,
                args=(self._shutdown_event,),
                daemon=True
            )
            camera_thread.start()

            # Запуск цикла отображения в главном потоке
            self.display_window.start_display(
                self.camera_manager.get_frame_queue(),
                self._shutdown_event
            )

            logger.info("Application started successfully")

            # Ожидание завершения потоков
            camera_thread.join(timeout=4.0)

        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Runtime error: {e}")
            raise ApplicationError(f"Application runtime error: {e}")
        finally:
            self.shutdown()

    def shutdown(self) -> None:
        """Завершение работы"""
        if not self.running:
            return

        logger.info("Shutting down application")
        self.running = False
        # Устанавливаем событие завершения для остановки потоков
        self._shutdown_event.set()

        # Чтобы поток отображения не пытался получить новые кадры из очереди сначала
        if self.camera_manager:
            # Прекратить поступление новых кадров
            self.camera_manager.stop_capture()

        if self.display_window:
            # Завершить отображение
            self.display_window.stop_display()

        logger.info("Application shutdown complete")

    def _signal_handler(self, signum: int, frame) -> None:
        """Обрабатывает системные сигналы для корректного завершения"""
        logger.info(f"Received signal {signum}, initiating shutdown")
        self.shutdown()
        sys.exit(0)


def main() -> None:

    env_file = Path(__file__).parent.parent / ".env"
    load_dotenv(env_file)

    logger.remove()
    logger.add(
        sys.stderr,
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{line} | {message}"
    )

    logger.info("Starting Video Capture Application")

    try:
        app = VideoApplication()
        app.initialize()
        app.run()

    except ApplicationError as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()