"""_summary_"""

import sys
from time import sleep

from digital_bomb.core.exp import show_exp
from digital_bomb.core.game import game
from digital_bomb.core.save_manager import load_game
from digital_bomb.utils.i18n import _
from digital_bomb.utils.clear_screen import clear_screen
from digital_bomb.utils.setup_logging import setup_logging, end_logger, clear_logs
from digital_bomb.config import CUT

logger = setup_logging(__name__)

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
                saves: list = load_game()
                
                if saves:

                    for save in saves:
                        print(_.t("index.saves", timestamp=save.timestamp, version=save.version,
                                  uuid=save.uuid, opponent=save.opponent, difficulty=save.difficulty,
                                  scope=save.scope, bomb=save.bomb, turn=save.turn,
                                  situation=save.situation, exp=save.exp))
                        print(CUT)

                show_exp()
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