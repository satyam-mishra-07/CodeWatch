import logging
import os
from typing import Optional


def setup_logging(
    level: Optional[str] = None,
    log_file: Optional[str] = None,
    logger_name: str = "",
) -> logging.Logger:
    """
    Configure application logging once and return the configured logger.

    - Creates log directory if it does not exist
    - Writes logs to both file and console
    - Prevents duplicate handlers if called multiple times
    """
    env_level = os.getenv("LOG_LEVEL", "INFO")
    env_log_file = os.getenv("LOG_FILE", "logs/review_agent.log")

    resolved_level = (level or env_level).upper()
    resolved_file = log_file or env_log_file

    logger = logging.getLogger(logger_name)
    logger.setLevel(getattr(logging, resolved_level, logging.INFO))

    # Avoid duplicate handler registration
    if logger.handlers:
        return logger

    os.makedirs(os.path.dirname(resolved_file) or ".", exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    file_handler = logging.FileHandler(resolved_file)
    file_handler.setLevel(getattr(logging, resolved_level, logging.INFO))
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, resolved_level, logging.INFO))
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a named logger after ensuring base logging is configured."""
    setup_logging()
    return logging.getLogger(name)
