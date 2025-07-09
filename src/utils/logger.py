import sys
from pathlib import Path

from loguru import logger


def setup_logging(log_level: str = "DEBUG") -> None:
    logger.remove()

    # Логирование в консоль
    logger.add(
        sys.stderr,
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{line} | {message}",
        colorize=True
    )

    # Логирование в файл
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    try:
        logger.add(
            log_dir / "app.log",
            level=log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{line} | {message}",
            rotation="1 day",
            retention="7 days",
            compression="gz"
        )
    except Exception as e:
        logger.warning(f"Failed to setup file logging: {e}")
