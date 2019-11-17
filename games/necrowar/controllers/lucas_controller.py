import logging
from ..game import Game
from ..player import Player
from .central_command import BaseController, UnitTypes

class LucasController(BaseController):
    def __init__(self, logger: logging.Logger, game: Game, player: Player):
        super().__init__(logger, game, player)
    
    def spawn_attackers(self):
        if self.can_afford_unit(self._jobs_by_title[str(UnitTypes.HOUND)]) == True:
            self.spawn_unit(UnitTypes.HOUND)
    
    def move_attackers(self):
        for unit in self.get_units(UnitTypes.HOUND):
            self.move_unit(unit, self.enemy_castle)

    def run_turn(self):
        self.spawn_attackers()
        self.move_attackers()
        self.logger.info(f'Hello from Lucas!')