import logging
from ..game import Game
from ..player import Player

class BaseController():
    def __init__(self, logger: logging.Logger, game: Game, player: Player):
        self._logger = logger
        self._game = game
        self._player = player
        logger.info(f'Starting game as {player.name}.')