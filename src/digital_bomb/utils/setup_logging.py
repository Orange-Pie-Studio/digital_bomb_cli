"""_summary_"""

import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from time import perf_counter, sleep
from datetime import datetime
from functools import wraps
from collections.abc import Callable
from typing import ParamSpec, TypeVar

from psutil import disk_partitions
from rich.progress import Progress, BarColumn, TextColumn
from rich.console import Console

from digital_bomb.utils.i18n import _
from digital_bomb.utils.resource_path import resource_path

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
    log_dir: Path = resource_path("logs")
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
                
            finally:
                end: float = perf_counter()
                logger.info(f"Function {func.__name__} executed in {end-start} seconds")
                
        return wrapper
        
    return decorator
    
logger = setup_logging(__name__)
    
@end_logger(logger)
def clear_logs() -> None:
    """_summary_"""
    log_files = []
    mountpoints = [Path(part.mountpoint) for part in disk_partitions()]

    for mountpoint in mountpoints:
        log_files += list(mountpoint.rglob("*.log*"))
    
    with Progress(
        TextColumn("[#66CCFF]{task.description}"),
        BarColumn(bar_width=42, style="#CD0000", complete_style="#00CD00"),
        TextColumn("• {task.completed}/{task.total} % "),
        console=Console()
    ) as progress:
        cache = []

        for f in log_files:

            try:
                step = f.stat().st_size
                cache.append(step)
                f.unlink(missing_ok=True)

            except FileNotFoundError as e:
                logger.exception(f"\n{e}")

            except Exception as e:
                cache.remove(step)
                logger.exception(f"\n{e}")

        if not cache:
            print(_.t("logs.delete_situation", count=sum(cache)))
            logger.info("No log")
            return

        task = progress.add_task(
            description=_.t("logs.delete"),
            total=100,
            completed=0
        )
        temp = 0

        for c in cache:
            temp += c
            progress.update(
                task,
                completed=int(temp / sum(cache) * 100)
            )
            sleep(0.01)

    print(_.t("logs.delete_situation", count=sum(cache)))
    logger.info(f"Deleted {sum(cache)} Bytes logs")