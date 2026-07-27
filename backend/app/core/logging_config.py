import logging


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    )


def get_logger(name: str = "app") -> logging.Logger:
    """Return a logger instance for the given name."""
    return logging.getLogger(name)
