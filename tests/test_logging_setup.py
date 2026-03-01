"""Unit tests for logging setup behavior."""

from __future__ import annotations

import logging
from pathlib import Path

from policygate.config.logging import setup_logging
from policygate.config.settings import Settings


def test_setup_logging_creates_log_directory_and_file(tmp_path: Path) -> None:
    root_logger = logging.getLogger()
    original_handlers = list(root_logger.handlers)
    original_level = root_logger.level
    had_configured_flag = hasattr(root_logger, "_policygate_logging_configured")
    original_configured_flag = getattr(
        root_logger,
        "_policygate_logging_configured",
        False,
    )

    try:
        root_logger.handlers.clear()
        root_logger._policygate_logging_configured = False

        log_file_path = tmp_path / "policygate" / "policygate.log"
        settings = Settings(log_file_path=str(log_file_path), log_level="INFO")

        setup_logging(settings)

        assert log_file_path.parent.exists()
        assert log_file_path.exists()

        logging.getLogger("policygate.test").info("log-check")
        for handler in root_logger.handlers:
            if hasattr(handler, "flush"):
                handler.flush()

        assert log_file_path.read_text(encoding="utf-8").strip() != ""
    finally:
        for handler in root_logger.handlers:
            if handler not in original_handlers:
                handler.close()
        root_logger.handlers.clear()
        root_logger.handlers.extend(original_handlers)
        root_logger.setLevel(original_level)

        if had_configured_flag:
            root_logger._policygate_logging_configured = original_configured_flag
        elif hasattr(root_logger, "_policygate_logging_configured"):
            delattr(root_logger, "_policygate_logging_configured")
