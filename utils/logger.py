"""Logging configuration for Discord Docs Bot."""

import logging
import sys
from pathlib import Path


def setup_logger(log_level: str = "INFO", log_file: str = "bot.log") -> logging.Logger:
    """
    Configure and return the application logger.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("DocsBot")
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create formatters
    detailed_formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    simple_formatter = logging.Formatter(
        "[%(levelname)s] %(message)s"
    )

    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)

    # File handler
    try:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not create log file {log_file}: {e}")

    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (default: DocsBot)

    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(f"DocsBot.{name}")
    return logging.getLogger("DocsBot")
