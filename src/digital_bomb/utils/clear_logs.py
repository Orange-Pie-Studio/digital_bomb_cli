from pathlib import Path
from asyncio import to_thread, gather

from psutil import disk_partitions

from digital_bomb.utils.i18n import _
from digital_bomb.utils.setup_logging import setup_logging, end_logger

logger = setup_logging(__name__)
    
@end_logger(logger)
def _clear_logs(mountpoint: Path) -> None:
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
    tasks = [to_thread(_clear_logs, mountpoint) for mountpoint in mountpoints]
    result = await gather(*tasks)
    flat = [item for sublist in result for item in sublist]
    print(_.t("logs.delete_situation", count=sum(flat)))