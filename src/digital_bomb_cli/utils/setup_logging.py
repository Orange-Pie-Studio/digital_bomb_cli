"""_summary_"""

import sys
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from time import perf_counter
from datetime import datetime
from functools import wraps
from collections.abc import Callable
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

def setup_logging(module_name: str) -> logging.Logger:
    """_summary_

    :param module_name: _description_
    :type module_name: str
    :return: _description_
    :rtype: logging.Logger
    """
    logger = logging.getLogger(module_name)
    
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    log_dir: Path = Path(sys.executable).parent / "logs" if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent.parent.parent.parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file: Path = log_dir / f"{module_name}.log"
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")

    file_handler = TimedRotatingFileHandler(
        log_file,
        when="midnight",
        utc=True,
        encoding="utf-8"
    )
    file_handler.namer = lambda default_name: f"logs/{datetime.now().strftime('%Y%m%d')}_{module_name}.log"
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

def end_logger(logger: logging.Logger) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """_summary_

    :param logger: _description_
    :type logger: logging.Logger
    :return: _description_
    :rtype: Callable[[Callable[P, R]], Callable[P, R]]
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
    
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            start: float = perf_counter()
            
            try:
                result: R = func(*args, **kwargs)
                return result
                
            except Exception as e:
                logger.exception(f"\n{e}")
                raise
                
            finally:
                end: float = perf_counter()
                logger.info(f"Function {func.__name__} executed in {end-start} seconds")
                
        return wrapper
        
    return decorator