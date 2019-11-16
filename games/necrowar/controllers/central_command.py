import logging
from enum import Enum, auto
from ..game import Game
from ..tile import Tile
from ..player import Player

class UnitTypes(Enum):
    WORKER = auto()
    ZOMBIE = auto()
    GHOUL = auto()
    HOUND = auto()
    ABOMINATION = auto()
    WRAITH = auto()
    HORSEMAN = auto()

    def __str__(self):
        mapping = {
            self.WORKER.value: 'worker',
            self.ZOMBIE.value: 'zombie',
            self.GHOUL.value: 'ghoul',
            self.HOUND.value: 'hound',
            self.ABOMINATION.value: 'abomination',
            self.WRAITH.value: 'wraith',
            self.HORSEMAN.value: 'horseman'
        }

        return mapping.get(self.value)

class BaseController():
    def __init__(self, logger: logging.Logger, game: Game, player: Player):
        self._logger = logger
        self._game = game
        self._player = player
        self._controllers = []
        self._worker_spawners = []
        self._unit_spawners = []

        for tile in game.tiles:
            if self.can_spawn_worker(tile):
                self._worker_spawners.append(tile)
            if self.can_spawn_unit(tile):
                self._unit_spawners.append(tile)
    
    def can_spawn_worker(self, tile):
        return tile.owner == self.player and tile.is_worker_spawn
    
    def can_spawn_unit(self, tile):
        return tile.owner == self.player and tile.is_unit_spawn
    
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
    def num_units(self):
        return len(self.player.units)

    @property
    def controllers(self):
        return self._controllers

    @property
    def workers_spawners(self):
        return self._worker_spawners

    @property
    def unit_spawners(self):
        return self._unit_spawners
    
    def add_controller(self, controller):
        self._controllers.append(controller)
        
    def run_turn(self):
        for controller in self.controllers:
            controller.run_turn()

    def select_spawner_for_unit(self, unit_type: UnitTypes):
        if unit_type == UnitTypes.WORKER and self.workers_spawners:
            return self.workers_spawners[0]
        elif self.unit_spawners:
            return self.unit_spawners[0]
            
        return None

    def spawn_unit(self, unit_type: UnitTypes, where=None):
        where: Tile = where if where is not None else \
                                    self.select_spawner_for_unit(unit_type)
        
        self.logger.info(f'Attempting to spawn unit type `{unit_type}`...')

        if where:
            unit_was_spawned = False

            if unit_type == UnitTypes.WORKER:
                unit_was_spawned = where.spawn_worker()
            else:
                unit_was_spawned = where.spawn_unit(str(unit_type))

            if unit_was_spawned:
                self.logger.info('Unit spawned successfully.')
            else:
                self.logger.warn('Failed to spawn unit.')
        else:
            self.logger.warn('No base was found for the current player.')