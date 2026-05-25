""" 
decorators.py
-------------------------
Shared logging helper for the data quality framework, such as logging execution time and handling exceptions.
"""

import time
from functools import wraps
from typing import Callable

from src.utils.logger import get_logger

logger = get_logger(__name__)

def log_execution(func: Callable) -> Callable:
    """ 
    Decorator to log the execution time of a function and handle exceptions.
    
    Usage:
        @log_execution
        def my_function(...):
            ...
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"Starting execution of {func.__qualname__}...")
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            execution_time = round(time.perf_counter() - start_time, 3)
            logger.info(f"Finished executing {func.__qualname__} in {execution_time} seconds.")
            return result
        except Exception as e:
            elapsed_time = round(time.perf_counter() - start_time, 3)
            logger.error(f"Error occurred while executing {func.__qualname__}: {e}. {elapsed_time}s seconds elapsed before error.")
            raise
    return wrapper
