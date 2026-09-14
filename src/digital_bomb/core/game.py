"""_summary_"""

from datetime import datetime
from random import randint
from time import sleep, time
from shutil import get_terminal_size

from readchar import readkey

from digital_bomb.core.GameAI import GameAI
from digital_bomb.core.exp import show_exp, calculate_exp
from digital_bomb.core.save_manager import GameState, save_game
from digital_bomb.utils.clear_screen import clear_screen
from digital_bomb.utils.setup_logging import setup_logging, end_logger
from digital_bomb.utils.i18n import _

logger = setup_logging(__name__)
CUT = "-" * get_terminal_size().columns

@end_logger(logger)
def game() -> None:
    """_summary_"""
    
    print(_.t("game.difficulty"))
    
    while True:
        
        match readkey():

            case "1":
                dif: str = "easy"
                break
        
            case "2":
                dif = "middle"
                break
        
            case "3":
                dif = "hard"
                break
            
    clear_screen()
    print(_.t("game.scope"))
    
    while True:
    
        match readkey():

            case "1":
                b: int = 100
                sco: str = "[0~100]"
                break

            case "2":
                b = 1000
                sco = "[0~1000]"
                break
        
            case "3":
                b = 10000
                sco = "[0~10000]"
                break
            
    clear_screen()
    
    a: int = 0
    x: int = randint(1, b-1)
    r: int = randint(0, 1)
    turn: int = 1
    keep_going: bool = True
    history: dict = {}
    
    ai: GameAI = GameAI(dif)
    ai.update(a, b)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    start_time: float = time()
    print(_.t("game.match"))
    sleep(1)
    print(_.t("game.vs", fake_name=ai.fake_name))
    print(_.t("game.choose"))
    sleep(1)
    
    if not r:
        first: str = _.t("game.you")
        print(f"\n{CUT}\n")
        print(_.t("game.choose_you", count=turn))
        
        try:
            c: float | int = float(input(f"{a} ～ {b}："))
            
            if not c.is_integer():
                raise ValueError(f"The input value {c} is an integer. Did you want to enter {int(c)}?")
            
            else:
                c = int(c)

        except ValueError as e:
            logger.exception(f"{e}\n")
            c = x

        r += 1

    else:
        first = ai.fake_name
        print(f"\n{CUT}\n")
        print(_.t("game.choose_ai", count=turn, fake_name=ai.fake_name))
        c = ai.guess()
        print(f'{a} ～ {b}：{c}')
        sleep(1)
        r -= 1
    
    while keep_going:
    
        while not r:
    
            if c != x and a < c < b:
                a, b = (c, b) if c < x else (a, c)
                history[turn] = dict(the_person_who_is_guessing=ai.fake_name, guess=c, new_range=(a, b))
                turn += 1
                print(f"\n{CUT}\n")
                print(_.t("game.turn_you", count=turn))
                
                try:
                    c = float(input(f"{a} ～ {b}："))
                    
                    if not c.is_integer():
                        raise ValueError(f"The input value {c} is an integer. Did you want to enter {int(c)}?")
                    
                    else:
                        c = int(c)
                
                except ValueError as e:
                    logger.exception(f"{e}\n")
                    c = x

                r += 1
    
            else:
                keep_going = False
                print(f"\n{CUT}\n")
                print(_.t("game.ai_bomb", fake_name=ai.fake_name))
                situation: str = "victory"
                break
    
        while r:
    
            if c != x and a < c < b:
                a, b = (c, b) if c < x else (a, c)
                history[turn] = dict(the_person_who_is_guessing=_.t("game.you"), guess=c, new_range=(a, b))
                turn += 1
                print(f"\n{CUT}\n")
                ai.update(a, b)
                print(_.t("game.turn_ai", count=turn, fake_name=ai.fake_name))
                c = ai.guess()
                print(f"{a} ～ {b}：{c}")
                r -= 1
    
            else:
                keep_going = False
                print(f"\n{CUT}\n")
                print(_.t("game.you_bomb"))
                situation = "defeat"
                break
                
    end_time: float = time()
    exp = calculate_exp(dif, turn, sco, situation)
    save_game(GameState(timestamp, int(end_time - start_time), ai.fake_name, dif, sco, first, turn, x, situation, exp, history))
    show_exp(exp)
    sleep(1.5)