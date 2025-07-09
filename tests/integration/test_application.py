from unittest.mock import patch

import pytest

from src.main import VideoApplication
from src.exceptions import ConfigurationError


class TestVideoApplication:
    def test_initialize_success(self, mock_env):
        """Тест успешной инициализации всего приложения"""
        with patch('src.camera.capture.cv2.VideoCapture'), \
                patch('src.display.window.cv2.namedWindow'):
            app = VideoApplication()
            app.initialize()
            assert app.config is not None
            assert app.camera_manager is not None
            assert app.display_window is not None

    def test_initialize_config_error(self):
        """Тест корректного сбоя инициализации при ошибке конфигурации"""
        with patch('src.main.Config', side_effect=ConfigurationError("Bad config")):
            with pytest.raises(ConfigurationError):
                app = VideoApplication()
                app.initialize()

    def test_run_and_shutdown(self, mock_env, mocker):
        """Тест основного цикла выполнения"""
        app = VideoApplication()

        # Мокируем зависимые от оборудования и блокирующие части
        mocker.patch('src.camera.capture.cv2.VideoCapture')
        mocker.patch('src.display.window.cv2.namedWindow')
        mocker.patch('src.display.window.cv2.imshow')
        mocker.patch('src.display.window.cv2.destroyAllWindows')

        # Мокируем блокирующий waitKey, чтобы позволить циклу выполниться
        mock_waitkey = mocker.patch('src.display.window.cv2.waitKey', return_value=ord('q'))

        # Мокируем долго выполняющиеся методы
        mock_cam_start = mocker.patch('src.camera.manager.CameraManager.start_capture')
        mock_display_start = mocker.patch('src.display.window.DisplayWindow.start_display')
        mock_cam_stop = mocker.patch('src.camera.manager.CameraManager.stop_capture')
        mock_display_stop = mocker.patch('src.display.window.DisplayWindow.stop_display')

        app.initialize()

        # Симулировать запуск так, чтобы он не блокировался навсегда.
        # Здесь просто проверка, вызываются ли правильные методы
        # Завершение, когда DisplayWindow возвращает управление после 'q'.
        def mock_run_display(*args, **kwargs):
            # Симулируем, что цикл отображения поработал и затем завершился
            app.display_window._handle_key_press(ord('q'))

        mock_display_start.side_effect = mock_run_display

        app.run()

        mock_cam_start.assert_called_once()
        mock_display_start.assert_called_once()

        # Метод shutdown должен быть вызван
        assert app._shutdown_event.is_set()
        mock_cam_stop.assert_called_once()
        mock_display_stop.assert_called_once()