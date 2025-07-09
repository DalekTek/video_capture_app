import os
import sys
from pathlib import Path
import threading
from queue import Queue
from unittest.mock import Mock, patch
import numpy as np
import pytest

sys.path.insert(0, os.path.abspath(Path(__file__).resolve().parents[1]))
sys.path.insert(0, os.path.abspath(Path(__file__).resolve().parents[0]))
from src.config import Config


@pytest.fixture
def mock_env():
    """Мок переменных"""
    with patch.dict(os.environ, {
        'CAMERA_INDEX': '0',
        'FRAME_WIDTH': '640',
        'FRAME_HEIGHT': '480',
        'FPS': '30',
        'WINDOW_TITLE': 'Test Window',
        'DISPLAY_SCALE': '1.0',
        'DEFAULT_FILTER': 'none',
        'FILTER_INTENSITY': '0.5',
        'MAX_QUEUE_SIZE': '10',
        'CAPTURE_TIMEOUT': '5.0',
        'LOG_LEVEL': 'DEBUG'
    }):
        yield


@pytest.fixture
def test_config(mock_env):
    """Создает тестовую конфигурацию"""
    return Config()


@pytest.fixture
def test_frame():
    """Создает тестовый кадр для обработки изображений"""
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    frame[:, :] = [100, 150, 200]  # BGR color
    return frame


@pytest.fixture
def frame_queue():
    """Создает тестовую очередь кадров"""
    queue = Queue(maxsize=10)
    return queue


@pytest.fixture
def shutdown_event():
    """Создает событие завершения тестирования"""
    return threading.Event()


@pytest.fixture
def mock_camera():
    """Мок камеры OpenCV (cv2.VideoCapture)"""
    with patch('cv2.VideoCapture') as MockVideoCapture:
        mock_instance = Mock()
        mock_instance.isOpened.return_value = True
        mock_instance.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
        mock_instance.set.return_value = True
        mock_instance.release.return_value = None
        MockVideoCapture.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_cv2_display():
    """Мок функции отображения OpenCV"""
    with patch('cv2.namedWindow') as mock_named_window, \
            patch('cv2.imshow') as mock_imshow, \
            patch('cv2.waitKey') as mock_waitkey, \
            patch('cv2.destroyAllWindows') as mock_destroy:
        mock_waitkey.return_value = 255  # Simulate no key press
        yield {
            "namedWindow": mock_named_window,
            "imshow": mock_imshow,
            "waitKey": mock_waitkey,
            "destroyAllWindows": mock_destroy
        }