"""_summary_"""

import json
from uuid import uuid4
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict

from digital_bomb.utils.setup_logging import setup_logging, end_logger
from digital_bomb.config import EXP_PATH, SAVE_DIR, __version__

logger = setup_logging(__name__)

@dataclass
class GameState:
    opponent: str
    difficulty: str
    scope: str
    turn: int
    bomb: int
    situation: str
    exp: int
    uuid: str = ""
    version: str = "0.0.0"
    timestamp: str = ""

    @end_logger(logger)
    def to_dict(self) -> dict:
        """_summary_

        :return: _description_
        :rtype: dict
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "GameState":
        """_summary_

        :param data: _description_
        :type data: dict
        :return: _description_
        :rtype: GameState
        """
        valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)

@end_logger(logger)
def save_game(state: GameState) -> None:
    """_summary_

    :param state: _description_
    :type state: GameState
    """
    state.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    state.uuid = str(uuid4())
    state.version = __version__
    save_path = SAVE_DIR / f"{state.timestamp}.json"

    try:
        save_path.write_text(
            json.dumps(state.to_dict(), ensure_ascii=False, indent=4),
            encoding='utf-8'
        )

    except OSError as e:
        logger.exception(f"\n{e}")

@end_logger(logger)
def load_game() -> list[GameState] | None:
    """_summary_

    :return: _description_
    :rtype: list[GameState] | None
    """
    files = sorted(SAVE_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime)

    if not files:
        return None
    
    state = []

    for path in files:

        try:
            raw_data = json.loads(path.read_text(encoding='utf-8'))
            state.append(GameState.from_dict(raw_data))
        
        except (json.JSONDecodeError, TypeError, KeyError, OSError) as e:
            logger.exception(f"\n{e}")

    return state

@end_logger(logger)
def save_exp(level: int, exp: int, max_exp: int) -> None:
    """_summary_

    :param level: _description_
    :type level: int
    :param exp: _description_
    :type exp: int
    :param max_exp: _description_
    :type max_exp: int
    """
    data = {
        "level": level,
        "exp": exp,
        "max_exp": max_exp
    }

    try:
        EXP_PATH.write_text(
            json.dumps(data, ensure_ascii=False, indent=4),
            encoding='utf-8'
        )

    except OSError as e:
        logger.exception(f"\n{e}")

@end_logger(logger)
def load_exp() -> dict[str, int]:
    """_summary_

    :return: _description_
    :rtype: dict[str, int]
    """

    try:
        return json.loads(EXP_PATH.read_text(encoding='utf-8'))
    
    except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
        logger.exception(f"\n{e}")
        return {}