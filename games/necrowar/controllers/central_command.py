import logging
from ..game import Game
from ..player import Player

class BaseController():
    def __init__(self, logger: logging.Logger, game: Game, player: Player):
        self._logger = logger
        self._game = game
        self._player = player
        self._controllers = []

    @property
    def logger(self):
        return self._logger
    
    @property
    def game(self):
        return self._game

    @property
    def player(self):
        return self._player

    @property
    def controllers(self):
        return self._controllers
    
    def add_controller(self, controller):
        self._controllers.append(controller)
        
    def run_turn(self):
        for controller in self.controllers:
            controller.run_turn()