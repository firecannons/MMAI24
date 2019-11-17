import logging
import heapq
import numpy as np
from enum import Enum, auto
from collections import defaultdict
from ..game import Game
from ..tile import Tile
from ..player import Player
from ..unit import Unit


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
        self._gold_mines = []
        self._gold_mine_coordinates = []
        self._units = defaultdict(list)
        self._jobs_by_title = {}
        self._enemy_castle = None

        for job in game.unit_jobs:
            self._jobs_by_title[job.title] = job

        for tile in game.tiles:
            if self.can_spawn_worker(tile):
                self._worker_spawners.append(tile)
            if self.can_spawn_unit(tile):
                self._unit_spawners.append(tile)
            if self.is_gold_mine(tile):
                self._gold_mines.append(tile)
                self._gold_mine_coordinates.append([tile.x, tile.y])
            if self.is_enemy_castle(tile):
                self._enemy_castle = tile
    
        self._gold_mine_coordinates = np.asarray(self._gold_mine_coordinates)

    def get_closest_gold_mine(self, unit):
        tile = self.get_tile_from(unit)
        coords = np.array([[tile.x, tile.y]])
        dist = self.distance_vectorized(coords, self._gold_mine_coordinates)
        closest_idx = np.argmin(dist)
        return self._gold_mines[closest_idx]
    
    def can_afford_unit(self, job):
        output = False
        if self.player.gold >= job.gold_cost and self.player.mana >= job.mana_cost:
            output = True
        return output
    
    def can_spawn_worker(self, tile):
        return tile.owner == self.player and tile.is_worker_spawn
    
    def can_spawn_unit(self, tile):
        return tile.owner == self.player and tile.is_unit_spawn

    def is_gold_mine(self, tile):
        return tile.is_gold_mine
    
    def is_enemy_castle(self, tile):
        return tile.is_castle == True and tile.owner != self.player
    
    @property
    def enemy_castle(self):
        return self._enemy_castle
        
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
    def workers(self):
        return self._units[UnitTypes.WORKER]

    @property
    def controllers(self):
        return self._controllers

    @property
    def worker_spawners(self):
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
        if unit_type == UnitTypes.WORKER and self.worker_spawners:
            return self.worker_spawners[0]
        elif self.unit_spawners:
            return self.unit_spawners[0]
            
        return None

    def get_tile_from(self, object):
        if hasattr(object, 'tile'):
            return object.tile
        elif isinstance(object, Tile):
            return object
        
        return None

    def move_cost(self, start, goal):
        return 1

    def distance_vectorized(self, start_coords, goal_coords):
        return np.sum(np.abs(start_coords - goal_coords), axis=1)

    def distance(self, start, goal):
        return np.abs(start.x-goal.x) + np.abs(start.y-goal.y)

    def _reconstruct_path(self, current_tile, came_from, start):
        path = [current_tile]

        while current_tile in came_from:
            current_tile = came_from[current_tile]

            if current_tile != start:
                path.insert(0, current_tile)
    
        return path
    
    def find_path(self, start, goal, f_metric=None):
        f_metric = f_metric if f_metric else self.distance
        
        start = self.get_tile_from(start)
        goal = self.get_tile_from(goal)
        visited = set(start.id)

        came_from = {}
        g_score = defaultdict(lambda: np.inf)
        g_score[start] = 0
        f_score = defaultdict(lambda: np.inf)
        f_score[start] = f_metric(start, goal)
        priority_queue = [(f_score[start], start.id, start)]

        while priority_queue:
            _, tile_id, current_tile = heapq.heappop(priority_queue)

            if current_tile == goal:
                return self._reconstruct_path(current_tile, came_from, start)
            
            for neighbor in current_tile.get_neighbors():
                score = g_score[current_tile] + self.move_cost(start, goal)

                if score < g_score[neighbor]:
                    came_from[neighbor] = current_tile
                    g_score[neighbor] = score
                    f_score[neighbor] = g_score[neighbor] + f_metric(current_tile, neighbor)
                    
                    if neighbor not in visited:
                        visited.add(neighbor.id)
                        heapq.heappush(priority_queue, (f_score[neighbor], neighbor.id, neighbor))
            
        return []

    def move_unit(self, unit: Unit, goal, number_of_moves=None):
        path = self.find_path(unit, goal)
        goal = self.get_tile_from(goal)

        if path and path[0] == goal:
            return 
        
        for i in range(len(path)):
            if unit.moves <= 0:
                break
        
            if not unit.move(path[i]):
                self.logger.warn(f'Failed to move unit `{unit.id}`.')
                break
            else:
                self.logger.info(f'Sucessfully moved unit of type `{unit.job.title}`')

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
                self._units[unit_type].append(where.unit)
            else:
                self.logger.warn('Failed to spawn unit.')
        else:
            self.logger.warn('No base was found for the current player.')

        return where


    def get_units(self, unit_type: UnitTypes):
        return self._units[unit_type]