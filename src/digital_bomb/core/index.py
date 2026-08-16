"""_summary_"""

import sys
from time import sleep
from shutil import get_terminal_size

from digital_bomb.core.exp import show_exp
from digital_bomb.core.game import game
from digital_bomb.core.save_manager import load_game
from digital_bomb.utils.i18n import _
from digital_bomb.utils.clear_screen import clear_screen
from digital_bomb.utils.setup_logging import setup_logging, end_logger, clear_logs

logger = setup_logging(__name__)

CUT = "-" * get_terminal_size().columns

@end_logger(logger)
def index() -> None:
    """_summary_"""

    while True:
        
        match input(_.t("index.index")):
        
            case '0':
                print(_.t("index.esc"))
                sleep(1)
                sys.exit(0)
            
            case '1':
                game()
                clear_screen()
            
            case '2':
                clear_screen()
                total_time, victory_time, saves = load_game()
                
                if saves:

                    for save in saves:
                        print(_.t("index.saves",version=save.version, uuid=save.uuid,
                                  timestamp=save.timestamp, game_time=save.game_time,
                                  opponent=save.opponent, difficulty=save.difficulty,
                                  scope=save.scope, bomb=save.bomb, first=save.first,
                                  turn=save.turn,situation=save.situation, exp=save.exp))
                        
                        for turn, message in save.history.items():
                            print(_.t("index.history.turn", turn=turn))

                            for msg in message.items():
                                print(_.t(f"index.history.{msg[0]}", msg=msg[1]))
                        
                        print(CUT)

                    show_exp()
                    print(_.t("index.game_data", total_game=len(saves), game_time=round(total_time/3600, 1),
                            victory_time=victory_time, win_rate=round(victory_time/len(saves)*100, 2)))
                    input(_.t("index.enter"))
                clear_screen()

            case "3":

                while True:

                    match input(_.t("index.setting")):

                        case "0":
                            clear_screen()
                            break

                        case "1":
                            clear_logs()
                            break