"""_summary_"""

from random import randint
from time import sleep

from digital_bomb.core.GameAI import GameAI
from digital_bomb.core.exp import show_exp, calculate_exp
from digital_bomb.core.save_manager import GameState, save_game
from digital_bomb.utils.setup_logging import setup_logging, end_logger
from digital_bomb.utils.i18n import _
from digital_bomb.config import CUT

logger = setup_logging(__name__)

@end_logger(logger)
def game() -> None:
    """_summary_"""
    
    while True:

        match input(_.t("game.difficulty")):
    
            case "1":
                dif: str = "easy"
                break
        
            case "2":
                dif = "middle"
                break
        
            case "3":
                dif = "hard"
                break
            
    while True:
    
        match input(_.t("game.scope")):
    
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
    
    a: int = 0
    x: int = randint(1, b-1)
    r: int = randint(0, 1)
    turn: int = 1
    keep_going: bool = True
    
    ai: GameAI = GameAI(dif)
    ai.update(a, b)
    
    print(_.t("game."))
    sleep(1)
    print(_.t("game.vs", fake_name=ai.fake_name))
    print(_.t("game.choose"))
    sleep(1)
    
    if not r:
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
        turn += 1

    else:
        print(f"\n{CUT}\n")
        print(_.t("game.choose_ai", count=turn, fake_name=ai.fake_name))
        c = ai.guess()
        print(f'{a} ～ {b}：{c}')
        sleep(1)
        r -= 1
        turn += 1
    
    while keep_going:
    
        while not r:
    
            if c != x and a < c < b:
                a, b = (c, b) if c < x else (a, c)
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
                turn += 1
    
            else:
                keep_going = False
                
                print(f"\n{CUT}\n")
                print(_.t("game.ai_bomb", fake_name=ai.fake_name))
                situation: str = "victory"
                break
    
        while r:
    
            if c != x and a < c < b:
                a, b = (c, b) if c < x else (a, c)
                print(f"\n{CUT}\n")
                ai.update(a, b)
                print(_.t("game.turn_ai", count=turn, fake_name=ai.fake_name))
                c = ai.guess()
                print(f"{a} ～ {b}：{c}")
                r -= 1
                turn += 1
    
            else:
                keep_going = False
                print(f"\n{CUT}\n")
                print(_.t("game.you_bomb"))
                situation = "defeat"
                break
                
    exp = calculate_exp(dif, turn, sco, situation)
    save_game(GameState(ai.fake_name, dif, sco, turn, x, situation, exp))
    show_exp(exp)
    sleep(1.5)