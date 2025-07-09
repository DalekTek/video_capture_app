import threading
from queue import Queue, Empty

import cv2
from loguru import logger

from ..config import Config
from ..exceptions import DisplayError
from ..filters.base import FilterFactory


class DisplayWindow:
    """Отображение видео и взаимодействие с user"""

    def __init__(self, config: Config):
        self.config = config
        self.window_name = config.window_title
        self.current_filter = FilterFactory.create(
            config.default_filter,
            config.filter_intensity
        )
        self.display_lock = threading.Lock()
        self.is_displaying = False

    def start_display(self, frame_queue: Queue, shutdown_event: threading.Event) -> None:
        """Запуск цикла отображения"""
        try:
            cv2.namedWindow(self.window_name, cv2.WINDOW_AUTOSIZE)
            logger.info(f"Display window created: {self.window_name}")

            self.is_displaying = True
            self._display_instructions()

            # Цикл отображения кадров пока не установлено событие завершения
            while not shutdown_event.is_set() and self.is_displaying:
                try:
                    # Получение кадра из очереди
                    # если в течение 0.1 секунды кадр не появится в очереди, будет выброшено исключение queue.Empty.
                    # Это позволяет циклу не блокироваться надолго, а регулярно проверять, не пришёл ли сигнал
                    # завершения. Таким образом, окно может быстро реагировать на завершение работы или другие события.
                    frame = frame_queue.get(timeout=0.1)

                    # Применение текущего фильтра
                    filtered_frame = self.current_filter.apply(frame)

                    # Масштабирование кадра при необходимости
                    if self.config.display_scale != 1.0:
                        new_width = int(filtered_frame.shape[1] * self.config.display_scale)
                        new_height = int(filtered_frame.shape[0] * self.config.display_scale)
                        # Изменение размера кадра с использованием линейной интерполяции
                        filtered_frame = cv2.resize(
                            filtered_frame,
                            (new_width, new_height),
                            interpolation=cv2.INTER_LINEAR
                        )

                    # Отображение кадра пока не установлено событие завершения
                    with self.display_lock:
                        cv2.imshow(self.window_name, filtered_frame)

                    # Обработка нажатий клавиш любых
                    key = cv2.waitKey(1) & 0xFF
                    if key != 255:              # Клавиша нажата
                        if not self._handle_key_press(key):
                            break

                except Empty:
                    continue
                except Exception as e:
                    logger.error(f"Display error: {e}")
                    break

        except Exception as e:
            logger.error(f"Display initialization error: {e}")
            raise DisplayError(f"Display failed: {e}")
        finally:
            self.stop_display()

    def stop_display(self) -> None:
        """Останавливает отображение и очищает ресурсы"""
        self.is_displaying = False

        try:
            with self.display_lock:
                cv2.destroyAllWindows()
            logger.info("Display stopped")
        except Exception as e:
            logger.error(f"Display cleanup error: {e}")

    def _handle_key_press(self, key: int) -> bool:
        """
            Обрабатывает ввод с клавиатуры. Возвращает False для выхода
            Здесь прописываем действия для клавиш
        """

        if key == ord('q') or key == 27:  # 'q'  или ESC
            logger.info("Exit key pressed")
            return False

        elif key == ord('1'):
            self._switch_filter("none")
        elif key == ord('2'):
            self._switch_filter("blur")
        elif key == ord('3'):
            self._switch_filter("sharpen")
        elif key == ord('4'):
            self._switch_filter("brightness")
        # elif key == ord('5'):                     # Добавьте свой фильтр здесь
        #    self._switch_filter("myfilter") ...
        elif key == ord('h'):
            self._display_instructions()

        return True

    def _switch_filter(self, filter_name: str) -> None:
        """Переключение на другой фильтр"""
        try:
            # При переключении фильтра создаётся новый объект фильтра с заданной интенсивностью
            self.current_filter = FilterFactory.create(
                filter_name,
                self.config.filter_intensity
            )
            logger.info(f"Switched to filter: {filter_name}")
        except Exception as e:
            logger.error(f"Failed to switch filter: {e}")

    def _display_instructions(self) -> None:
        """Отображение инструкции для user"""
        instructions = [
            "=== Video Capture Controls ===",
            "Press '1' - No filter",
            "Press '2' - Blur filter",
            "Press '3' - Sharpen filter",
            "Press '4' - Brightness filter",
            # "Press '5' - My custom filter",  # Добавьте свой фильтр здесь
            "Press 'h' - Show this help",
            "Press 'q' or ESC - Exit",
            "=============================="
        ]

        for instruction in instructions:
            logger.info(instruction)