"""Logging utility"""

import logging
import sys
from typing import Optional
from app.config.settings import get_settings


def setup_logging(level: Optional[str] = None) -> None:
    """Setup application logging"""
    settings = get_settings()
    log_level = level or ("DEBUG" if settings.DEBUG else "INFO")
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def get_logger(name: str) -> logging.Logger:
    """Get logger instance"""
    return logging.getLogger(name)

