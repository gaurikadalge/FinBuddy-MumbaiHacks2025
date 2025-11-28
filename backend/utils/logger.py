# backend/utils/logger.py

import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from backend.core.config import settings

def setup_logger():
    logger = logging.getLogger("FinBuddy")

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # ---------------------------------------------------------
    # FORMATTER (dev = colored, prod = plain)
    # ---------------------------------------------------------
    if settings.APP_ENV.lower() == "development":
        try:
            import colorlog
            formatter = colorlog.ColoredFormatter(
                "%(log_color)s%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                "%Y-%m-%d %H:%M:%S",
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "bold_red",
                }
            )
        except:
            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                "%Y-%m-%d %H:%M:%S"
            )
    else:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            "%Y-%m-%d %H:%M:%S"
        )

    # ---------------------------------------------------------
    # STREAM HANDLER (Console)
    # ---------------------------------------------------------
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    try:
        if hasattr(stream_handler.stream, "reconfigure"):
            stream_handler.stream.reconfigure(encoding="utf-8")
    except:
        pass

    logger.addHandler(stream_handler)

    # ---------------------------------------------------------
    # FILE HANDLER (Prod only)
    # ---------------------------------------------------------
    if settings.APP_ENV.lower() == "production":
        os.makedirs("logs", exist_ok=True)
        file_handler = RotatingFileHandler(
            "logs/finbuddy.log",
            maxBytes=2 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


logger = setup_logger()
