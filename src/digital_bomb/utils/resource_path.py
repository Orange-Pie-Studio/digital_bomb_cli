"""_summary_"""

import sys
from pathlib import Path

def resource_path(relative_path: str) -> Path:
    """_summary_

    :param relative_path: _description_
    :type relative_path: str
    :return: _description_
    :rtype: Path
    """

    if getattr(sys, 'frozen', False):
        base_path = Path(sys._MEIPASS)

    else:
        base_path = Path(__file__).resolve().parent.parent.parent.parent
    
    return base_path / relative_path