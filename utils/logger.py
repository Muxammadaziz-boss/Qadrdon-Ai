"""Qadirdon AI — Logging sozlamalari."""

import sys

from loguru import logger

from config.settings import settings


def setup_logger() -> None:
    """Loguru loggerini sozlash."""
    logger.remove()

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    logger.add(
        sys.stderr,
        format=log_format,
        level=settings.LOG_LEVEL,
        colorize=True,
    )

    logger.add(
        "logs/qadirdon_{time:YYYY-MM-DD}.log",
        format=log_format,
        level="DEBUG",
        rotation="1 day",
        retention="30 days",
        compression="zip",
    )

