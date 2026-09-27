"""
Logging configuration for CostScope.

The logging configuration provides:

1. Human-readable console logging.
2. Persistent log files.
3. Automatic log rotation.
4. A consistent logging format across pipeline modules.

Example
-------
from data_pipeline.utils.logging_config import get_logger

logger = get_logger(__name__)
logger.info("Starting dataset extraction")
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from data_pipeline.config.settings import settings

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_logging() -> None:
    """
    Configure root logging for the CostScope application.

    Logs are written to both:

    - stdout / PyCharm terminal
    - logs/costscope.log

    The file logger rotates automatically after reaching approximately
    5 MB to prevent unlimited local log growth.
    """

    log_directory: Path = settings.logs_path
    log_directory.mkdir(parents=True, exist_ok=True)

    log_file = log_directory / "costscope.log"

    root_logger = logging.getLogger()

    # Prevent duplicate handlers if this function is called more than once.
    if root_logger.handlers:
        return

    log_level = getattr(
        logging,
        settings.log_level.upper(),
        logging.INFO,
    )

    root_logger.setLevel(log_level)

    formatter = logging.Formatter(
        LOG_FORMAT,
        datefmt=DATE_FORMAT,
    )

    # ---------------------------------------------------------
    # Console handler
    # ---------------------------------------------------------
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    # ---------------------------------------------------------
    # Rotating file handler
    # ---------------------------------------------------------
    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=5_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Return a configured logger.

    Parameters
    ----------
    name:
        Usually pass ``__name__`` so logs show the module responsible
        for each message.

    Returns
    -------
    logging.Logger
        Configured Python logger.
    """

    configure_logging()

    return logging.getLogger(name)
