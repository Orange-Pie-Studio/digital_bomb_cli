"""_summary_"""

from random import randint
from time import sleep

from faker import Faker

from digital_bomb.utils.setup_logging import setup_logging, end_logger

logger = setup_logging(__name__)

class GameAI:
    """_summary_"""
    
    def __init__(self, difficulty: str) -> None:
        """_summary_

        :param difficulty: _description_
        :type difficulty: str
        """
        self.difficulty: str = difficulty
        self.fake_name = Faker().name()

    @end_logger(logger)
    def update(self, a: int, b: int) -> None:
        """_summary_

        :param a: _description_
        :type a: int
        :param b: _description_
        :type b: int
        """
        self.a: int = a
        self.b: int = b

    @end_logger(logger)
    def guess(self) -> int:
        """_summary_

        :return: _description_
        :rtype: int
        """
        sleep(randint(1, 2))
        
        match self.difficulty:
        
            case "easy":
                return randint(self.a+1, self.b-1)
            
            case "middle":
        
                if randint(1, 10) < 7:
                    return (self.a+self.b) // 2
                
                else:
                    return randint(self.a+1, self.b-1)
                
            case "hard":
                return (self.a+self.b) // 2