"""_summary_"""

import sys
from subprocess import run

from digital_bomb_cli.utils.setup_logging import setup_logging, end_logger

logger = setup_logging(__name__)

@end_logger(logger)
def clear_screen() -> None:
    """_summary_"""

    try:
    
        match sys.platform:
        
            case "win32":
                run(["cmd", "/c", "cls"])
            
            case _:
                run(["/usr/bin/clear"])
                
        sys.stdout.flush()
                
    except (FileNotFoundError, OSError) as e:
        logger.exception(f"\n{e}")