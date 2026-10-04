"""_summary_"""

from datetime import datetime
from random import randint
from time import sleep
from shutil import get_terminal_size

from readchar import readkey

from digital_bomb_cli.core.GameAI import GameAI
from digital_bomb_cli.core.exp import show_exp, calculate_exp
from digital_bomb_cli.core.save_manager import GameState, save_game
from digital_bomb_cli.utils.clear_screen import clear_screen
from digital_bomb_cli.utils.setup_logging import setup_logging, end_logger
from digital_bomb_cli.utils.i18n import _

logger = setup_logging(__name__)
CUT = "-" * get_terminal_size().columns

class Game:
    """_summary_"""
    
    def __init__(self) -> None:
        self.difficulty: str = ""
        self.scope: str = ""
        self.a: int = 0
        self.b: int = 0
        self.c: int = 0
        self.x: int = 0
        self.round: int = 1
        self.turn: bool = True
        self.keep_going: bool = True
        self.ai: GameAI | None = None
        self.timestamp: str = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.history: dict = {}
        
    @end_logger(logger)
    def _choose_difficulty(self) -> None:
        """_summary_"""
        
        print(_.t("game.difficulty"))
        
        while True:
            
            match readkey():
    
                case "1":
                    self.difficulty = "easy"
                    break
            
                case "2":
                    self.difficulty = "middle"
                    break
            
                case "3":
                    self.difficulty = "hard"
                    break
                
        clear_screen()
        
    @end_logger(logger)
    def _choose_scope(self) -> None:
        """_summary_"""
        
        print(_.t("game.scope"))
        
        while True:
            
            match readkey():
    
                case "1":
                    self.b = 100
                    self.scope: str = "[0~100]"
                    break
    
                case "2":
                    self.b = 1000
                    self.scope = "[0~1000]"
                    break
            
                case "3":
                    self.b = 10000
                    self.scope = "[0~10000]"
                    break
                
        clear_screen()
                
    @end_logger(logger)
    def _setup_game(self) -> None:
        """_summary_"""
        
        self.x = randint(self.a + 1, self.b - 1)
        self.ai = GameAI(self.difficulty)
        self.ai.update(self.a, self.b)
        
        print(_.t("game.vs", fake_name=self.ai.fake_name))
        print(_.t("game.choose"))
        self.turn = True if randint(0, 1) == 0 else False
        sleep(1)
        clear_screen()
            
    @end_logger(logger)
    def _player_turn(self) -> None:
        """_summary_"""
        
        print(_.t("game.turn_you", count=self.round))
        
        try:
            self.c: int = int(input(f"{self.a} ～ {self.b}："))

        except (ValueError, EOFError) as e:
            logger.exception(f"{e}\n")
            self.c = self.x

        self.turn = False
        
    @end_logger(logger)
    def _ai_turn(self) -> None:
        """_summary_"""
        
        self.ai.update(self.a, self.b)
        print(_.t("game.turn_ai", count=self.round, fake_name=self.ai.fake_name))
        self.c = self.ai.guess()
        print(f"{self.a} ～ {self.b}：{self.c}")
        sleep(1)
        self.turn = True
        
    @end_logger(logger)
    def _update_range(self) -> None:
        
        """_summary_"""
        self.history[self.round] = dict(the_person_who_is_guessing=self.ai.fake_name if self.turn else _.t("game.you"), new_range=(self.a, self.b), guess=self.c)
        
        if self.c != self.x and self.a < self.c < self.b:
            self.a, self.b = (self.c, self.b) if self.c < self.x else (self.a, self.c)
            
        else:
            self.keep_going = False
            
            if self.turn:
                print(_.t("game.ai_bomb", fake_name=self.ai.fake_name))
                self.situation = "victory"
                
            else:
                print(_.t("game.you_bomb"))
                self.situation = "defeat"
            
            self.exp = calculate_exp(self.difficulty, self.round, self.scope, self.situation)
            show_exp(self.exp)
            sleep(1.5)
            
    @end_logger(logger)
    def _play(self) -> None:
        """_summary_"""
            
        if self.turn:
            self._player_turn()
            
        else:
            self._ai_turn()
            
        print(f"{CUT}\n")
        self._update_range()
        self.round += 1
        
    @end_logger(logger)
    def run(self) -> None:
        """_summary_"""
        
        self._choose_difficulty()
        self._choose_scope()
        self._setup_game()
        
        while self.keep_going:
            self._play()
        
        save_game(GameState(self.timestamp,
                            self.ai.fake_name,
                            self.difficulty,
                            self.scope,
                            _.t("game.you") if self.turn else self.ai.fake_name,
                            self.round-1,
                            self.x,
                            self.situation,
                            self.exp,
                            self.history
                            )
                  )