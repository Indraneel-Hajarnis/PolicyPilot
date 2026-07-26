"""
Structured logging configuration for PolicyPilot.
"""

import logging
import sys
from typing import Optional


def setup_logging(level: int = logging.INFO) -> None:
    """
    Configure structured logging for the application.

    Sets up separate loggers for api, services, and db layers
    with a unified format including timestamps and module paths.
    """
    log_format = (
        "%(asctime)s │ %(levelname)-8s │ %(name)-20s │ %(message)s"
    )
    date_format = "%Y-%m-%d %H:%M:%S"

    formatter = logging.Formatter(fmt=log_format, datefmt=date_format)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)

    # Root logger
    root_logger = logging.getLogger("policypilot")
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    root_logger.propagate = False

    # Silence noisy third-party loggers
    for noisy in ("httpx", "httpcore", "urllib3", "sentence_transformers"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a named logger under the policypilot namespace.

    Args:
        name: Logger name suffix (e.g., "api", "services.embedder").
              If None, returns the root policypilot logger.

    Returns:
        A configured Logger instance.
    """
    if name:
        return logging.getLogger(f"policypilot.{name}")
    return logging.getLogger("policypilot")
