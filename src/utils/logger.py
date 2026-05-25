""" 
logger.py
-------------
Centralized logging utility for the data quality framework.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

_LOG_DIR = Path("logs")
_LOG_FILE = _LOG_DIR / "dq_framework.log"
_FORMAT = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def get_logger(name: str) -> logging.Logger:
    """ 
   Returns a named logger with both console and rotating file handlers.
    
    Args:
        name (str): The name of the logger, typically __name__ of the module.
        
    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)

    # prevent adding multiple handlers if logger already has handlers (e.g., in interactive environments)
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(_FORMAT,datefmt=_DATE_FORMAT)

    # Console handler - INFO and above
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Rotating File handler - DEBUG and above (full traces for ops)
    _LOG_DIR.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(_LOG_FILE, maxBytes=5*1024*1024, backupCount=5, encoding='utf-8')  # 5MB per file, keep 5 backups
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger
