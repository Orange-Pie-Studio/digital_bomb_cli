"""_summary_"""

import sys
from time import sleep
from shutil import get_terminal_size
from asyncio import run

from readchar import readkey

from digital_bomb_cli.core.exp import show_exp
from digital_bomb_cli.core.game import Game
from digital_bomb_cli.core.save_manager import load_game
from digital_bomb_cli.utils.i18n import _
from digital_bomb_cli.utils.clear_screen import clear_screen
from digital_bomb_cli.utils.setup_logging import setup_logging, end_logger
from digital_bomb_cli.utils.clear_logs import main_clear_logs

logger = setup_logging(__name__)

CUT = "-" * get_terminal_size().columns

@end_logger(logger)
def index() -> None:
    """_summary_"""

    print(_.t("index.index"))
    
    match readkey():
    
        case '0':
            print(_.t("index.esc"))
            sleep(1)
            sys.exit(0)
        
        case '1':
            clear_screen()
            Game().run()
            clear_screen()
        
        case '2':
            clear_screen()
            victory_time, saves = load_game()
            
            if saves:

                for save in saves:
                    print(_.t("index.saves",version=save.version, uuid=save.uuid,
                              timestamp=save.timestamp, opponent=save.opponent, difficulty=save.difficulty,
                              scope=save.scope, bomb=save.bomb, first=save.first,
                              turn=save.turn, situation=save.situation, exp=save.exp))
                    
                    for turn, message in save.history.items():
                        print(_.t("index.history.turn", turn=turn))

                        for msg in message.items():
                            print(_.t(f"index.history.{msg[0]}", msg=msg[1]))
                    
                    print(CUT)

                show_exp()
                print(_.t("index.game_data", total_game=len(saves),
                          victory_time=victory_time, win_rate=round(victory_time/len(saves)*100, 2)))
                input(_.t("index.enter"))
                
            clear_screen()

        case "3":
            clear_screen()
            print(_.t("index.setting"))

            match readkey():

                case "0":
                    clear_screen()

                case "1":
                    clear_screen()
                    run(main_clear_logs(), debug=True)
                    
                case _:
                    clear_screen()
                    
        case _:
            clear_screen()