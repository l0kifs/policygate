"""Logging configuration utilities for policygate."""

from __future__ import annotations

import logging
import logging.handlers
from pathlib import Path

from policygate.config.settings import Settings

logger = logging.getLogger("policygate")


def setup_logging(settings: Settings) -> None:
    """Configure process-wide logging to stderr and file."""
    root_logger = logging.getLogger()
    if getattr(root_logger, "_policygate_logging_configured", False):
        return

    log_file_path = Path(settings.log_file_path).expanduser().resolve()
    log_file_path.parent.mkdir(parents=True, exist_ok=True)

    log_level_name = settings.log_level.upper()
    log_level = getattr(logging, log_level_name, logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(log_level)
    stream_handler.setFormatter(formatter)

    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_file_path,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    root_logger.setLevel(log_level)
    root_logger.handlers.clear()
    root_logger.addHandler(stream_handler)
    root_logger.addHandler(file_handler)
    root_logger._policygate_logging_configured = True
