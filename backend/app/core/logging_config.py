"""
Logging configuration for the CostScope FastAPI backend.
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from backend.app.core.config import PROJECT_ROOT

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_api_logging() -> None:
    """Configure console and rotating file logging for the API."""

    root_logger = logging.getLogger()

    # Logging may already have been configured by Uvicorn or another
    # application component.
    if any(
        getattr(handler, "_costscope_handler", False)
        for handler in root_logger.handlers
    ):
        return

    root_logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        LOG_FORMAT,
        datefmt=DATE_FORMAT,
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler._costscope_handler = True  # type: ignore[attr-defined]

    log_directory = Path(PROJECT_ROOT) / "logs"
    log_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_handler = RotatingFileHandler(
        log_directory / "costscope_api.log",
        maxBytes=5_000_000,
        backupCount=5,
        encoding="utf-8",
    )

    file_handler.setFormatter(formatter)
    file_handler._costscope_handler = True  # type: ignore[attr-defined]

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)


def get_api_logger(name: str) -> logging.Logger:
    """Return a configured API logger."""

    configure_api_logging()

    return logging.getLogger(name)
