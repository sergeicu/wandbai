"""Logging configuration for Query.ai application."""

import sys
from pathlib import Path
from loguru import logger
import os


def setup_logger(log_level: str = None, log_file: str = None):
    """
    Configure application logging.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (if None, logs only to console)
    """
    # Remove default handler
    logger.remove()

    # Get log level from env or parameter
    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO")

    # Console handler with custom format
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True,
    )

    # File handler if specified
    if log_file is None:
        log_file = os.getenv("LOG_FILE")

    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=log_level,
            rotation="10 MB",  # Rotate when file reaches 10MB
            retention="7 days",  # Keep logs for 7 days
            compression="zip",  # Compress rotated logs
        )

    logger.info(f"Logger initialized with level: {log_level}")
    return logger


def get_logger(name: str):
    """
    Get a logger instance with the given name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logger.bind(name=name)


# Initialize default logger
setup_logger()
