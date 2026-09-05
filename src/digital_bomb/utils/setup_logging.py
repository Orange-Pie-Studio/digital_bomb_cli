"""_summary_"""

import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from time import perf_counter
from datetime import datetime
from functools import wraps
from asyncio import gather, to_thread
from collections.abc import Callable
from typing import ParamSpec, TypeVar

from psutil import disk_partitions

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
def clear_logs(mountpoint: Path) -> None:
    """_summary_

    :param mountpoint: _description_
    :type mountpoint: Path
    """
    log_files: list[Path] = list(mountpoint.rglob("*.log"))
    total_size: list[int] = []

    for file in log_files:

        try:

            if file.is_symlink() or file.is_dir() or not file.exists():
                continue

            step: int = file.stat().st_size
            file.unlink(missing_ok=True)

        except PermissionError as e:
            logger.exception(f"\n{e}")

        else:
            total_size.append(step)

    logger.info(f"{mountpoint} deleted done.")
    return total_size

@end_logger(logger)
async def main_clear_logs() -> None:
    """_summary_"""
    mountpoints: list[Path] = [Path(part.mountpoint) for part in disk_partitions() if part.fstype]
    print(_.t("logs.delete_tips"))
    tasks = [to_thread(clear_logs, mountpoint) for mountpoint in mountpoints]
    result = await gather(*tasks)
    flat = [item for sublist in result for item in sublist]
    print(_.t("logs.delete_situation", count=sum(flat)))