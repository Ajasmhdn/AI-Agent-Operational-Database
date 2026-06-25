"""
logger.py

Central logging configuration for Sprint 2 data generation.

Responsibilities:
- Create logs directory automatically
- Log to both console and file
- Separate error-only log file
- Standardized formatting
- Reusable logger instance
"""

import logging
from pathlib import Path

# ============================================================
# CREATE LOG DIRECTORY
# ============================================================

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE       = LOG_DIR / "generation.log"
ERROR_LOG_FILE = LOG_DIR / "errors.log"

# ============================================================
# LOGGER CONFIGURATION
# ============================================================

LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)s | "
    "%(name)s | "
    "%(message)s"
)

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ============================================================
# CREATE LOGGER
# ============================================================

logger = logging.getLogger("ops_insights")

# Prevent duplicate handlers on re-import
if not logger.handlers:

    logger.setLevel(logging.INFO)

    # ----------------------------
    # Formatter
    # ----------------------------

    formatter = logging.Formatter(
        fmt=LOG_FORMAT,
        datefmt=DATE_FORMAT
    )

    # ----------------------------
    # File Handler — Full Log
    # ----------------------------

    file_handler = logging.FileHandler(
        filename=LOG_FILE,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # ----------------------------
    # File Handler — Errors Only
    # ----------------------------

    error_handler = logging.FileHandler(
        filename=ERROR_LOG_FILE,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    # ----------------------------
    # Console Handler
    # ----------------------------

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # ----------------------------
    # Register Handlers
    # ----------------------------

    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)

# Prevent propagation to root logger
logger.propagate = False