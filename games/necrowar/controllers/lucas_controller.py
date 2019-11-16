import logging
from ..game import Game
from ..player import Player
from .central_command import BaseController

class LucasController(BaseController):
    def __init__(self, logger: logging.Logger, game: Game, player: Player):
        super().__init__(logger, game, player)

    def run_turn(self):
        self.logger.info(f'Hello from Lucas!')
    
    def can_afford_unit(self, job):
        output = False
        if self.player.gold >= job.gold_cost and self.player.mana >= job.mana_cost:
            output = True
        return output