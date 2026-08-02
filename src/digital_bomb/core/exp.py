"""_summary_"""

from time import sleep
from random import randint

from rich.progress import Progress, BarColumn, TextColumn
from rich.console import Console

from digital_bomb.core.save_manager import save_exp, load_exp
from digital_bomb.utils.setup_logging import setup_logging, end_logger

logger = setup_logging(__name__)

@end_logger(logger)
def show_exp(delta_exp: int | None = None) -> None:
    """_summary_

    :param delta_exp: _description_, defaults to None
    :type delta_exp: int | None, optional
    """
    archive: dict[str, int] = load_exp()
    exp: int = archive.get("exp", 0)
    max_exp: int = archive.get("max_exp", 1000)
    level: int = archive.get("level", 1)
    
    with Progress(
        TextColumn("[#66CCFF]{task.description}"),
        BarColumn(bar_width=42, style="#CD0000", complete_style="#00CD00"),
        TextColumn("• {task.completed}/{task.total} XP"),
        console=Console()
    ) as progress:
        task = progress.add_task(
            description=f'Lv.{level}',
            total=max_exp,
            completed=exp
        )

        if delta_exp is not None:

            while delta_exp > 0:
                need_to_next: int = max_exp - exp
                step: int = min(randint(75, 100), delta_exp, need_to_next)
                exp += step
                delta_exp -= step
                progress.update(
                    task,
                    description=f"Lv.{level}",
                    total=max_exp,
                    completed=exp
                )
                sleep(0.01)

                if exp >= max_exp:
                    overflow: int = exp - max_exp
                    level += 1
                    max_exp = int(1000 * (level ** 1.1))
                    exp = overflow if overflow > 0 else 0
                    progress.update(
                        task,
                        description=f"Lv.{level}",
                        total=max_exp,
                        completed=exp
                    )
    
    save_exp(level, exp, max_exp)

@end_logger(logger)
def calculate_exp(difficult: str, turn: int, scope: str, situation: str) -> int:
    """_summary_

    :param difficult: _description_
    :type difficult: str
    :param turn: _description_
    :type turn: int
    :param scope: _description_
    :type scope: str
    :param situation: _description_
    :type situation: str
    :return: _description_
    :rtype: int
    """

    match difficult:
        
        case "easy":
            difficulty = 4
            
        case "middle":
            difficulty = 7

        case "hard":
            difficulty = 10

        case _:
            difficulty = 1

    match scope:
        
        case "[0~100]":
            simple_turns = 10
            
        case "[0~1000]":
            simple_turns = 15

        case "[0~10000]":
            simple_turns = 25

        case _:
            simple_turns = 1

    turns = (simple_turns / turn) if situation == "victory" else (turn / simple_turns)
    return int(1000 * difficulty * turns * (1 if situation == "victory" else 0.1))