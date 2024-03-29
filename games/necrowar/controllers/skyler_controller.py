import logging
from ..game import Game
from ..player import Player
from .central_command import BaseController

class SkylerController(BaseController):
    def __init__(self, logger: logging.Logger, game: Game, player: Player):
        super().__init__(logger, game, player)

    def run_turn(self):
        self.logger.info('Hello from Skyler!')