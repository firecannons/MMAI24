import logging
from ..game import Game
from ..player import Player
from .central_command import BaseController, UnitTypes

class ChrisController(BaseController):
    def __init__(self, logger: logging.Logger, game: Game, player: Player):
        super().__init__(logger, game, player)
        logger.info(f'Starting game as {player.name}.')

    def run_turn(self):
        #print('-'*140)
        #self.logger.info(f'On turn #{self.game.current_turn}')
        
        if not self.num_units:
            self.spawn_unit(UnitTypes.WORKER)

        for worker in self.get_units(UnitTypes.WORKER):
            self.move_unit(worker, self.get_closest_gold_mine(worker))