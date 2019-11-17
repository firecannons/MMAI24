import logging
import heapq
import numpy as np
from enum import Enum, auto
from collections import defaultdict
from ..game import Game
from ..tile import Tile
from ..player import Player
from ..unit import Unit
import random


class UnitTypes(Enum):
    WORKER = auto()
    ZOMBIE = auto()
    GHOUL = auto()
    HOUND = auto()
    ABOMINATION = auto()
    WRAITH = auto()
    HORSEMAN = auto()
    reverse_mapping = None

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
        self._unit_types = {
            'worker': UnitTypes.WORKER,
            'zombie': UnitTypes.ZOMBIE,
            'ghoul': UnitTypes.GHOUL,
            'hound': UnitTypes.HOUND,
            'abomination': UnitTypes.ABOMINATION,
            'wraith': UnitTypes.WRAITH,
            'horseman': UnitTypes.HORSEMAN
        }
        self._tower_types = {
            'arrow': 'arrow',
            'ballista': 'ballista',
            'cleansing': 'cleansing',
            'aoe': 'aoe',
            'castle': 'castle',
        }
        self._enemy_castle = None
        self.miners = []
        self.fishers = []
        self.builders = []

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
    
    def select_random_tower_type(self):
        choice = random.choice(list(self._tower_types))
        while choice == 'castle':
            choice = random.choice(list(self._tower_types))
        return choice
    
    def spawn_builder(self):
        if self.can_afford_unit(self._jobs_by_title[str(UnitTypes.WORKER)]) and len(self.builders) == 0:
            if self.select_spawner_for_unit(UnitTypes.WORKER).unit == None:
                tile = self.spawn_unit(UnitTypes.WORKER)
                if tile.unit:
                    self.builders.append(tile.unit)
    
    def control_builders(self):
        for worker in self.builders:
            self.move_unit(worker, self.get_next_tower_tile(worker))
            if worker.tile.id == self.get_next_tower_tile(worker).id:
                worker.build(self.select_random_tower_type())
    
    def get_next_tower_tile(self, worker):
        corner_tile = self.get_tower_corner(worker)
        x = corner_tile.x
        y = corner_tile.y
        found_tile = False
        tile = None
        while found_tile == False:
            if self.game.tiles[corner_tile.x + y * self.game.map_width].tower == None:
                found_tile = True
                tile = self.game.tiles[corner_tile.x + y * self.game.map_width]
            else:
                if corner_tile.x < self.game.map_width / 2:
                    x = x + 1
                else:
                    x = x - 1
                if self.game.tiles[x + corner_tile.y * self.game.map_width].tower == None:
                    found_tile = True
                    tile = self.game.tiles[x + corner_tile.y * self.game.map_width]
                else:
                    if corner_tile.y < self.game.map_height / 2:
                        y = y + 1
                    else:
                        y = y - 1
        return tile
    
    def get_tower_corner(self, worker):
        x = 0
        y = 0
        if worker.tile.x < self.game.map_width / 2:
            x = 7
            y = self.game.map_height - 7 - 1
        else:
            x = self.game.map_width - 7 - 1
            y = 7
        return self.game.tiles[x + y * self.game.map_width]

    def spawn_fisher(self):
        if self.can_afford_unit(self._jobs_by_title[str(UnitTypes.WORKER)]):
            if self.select_spawner_for_unit(UnitTypes.WORKER).unit == None:
                tile = self.spawn_unit(UnitTypes.WORKER)
                if tile.unit:
                    self.fishers.append(tile.unit)
    
    def find_nearest_shore(self, unit):
        x = 0
        y = unit.tile.y
        if unit.tile.x > self.game._map_width / 2:
            x = int(self.game._map_width / 2) + 2
        else:
            x = int(self.game._map_width / 2) - 2
        if unit.tile.y < self.game._map_height / 2:
            while self.game.tiles[x + y * self.game.map_width].unit:
                y = y + 1
        else:
            while self.game.tiles[x + y * self.game.map_width].unit:
                y = y - 1
        return self.game.tiles[x + y * self.game.map_width]

    def control_fishers(self):
        for worker in self.fishers:
            foundwater = False
            for neighbor in worker.tile.get_neighbors():
                if neighbor.is_river:
                    foundwater = True
                    worker.fish(neighbor)
            if foundwater == False:
                self.move_unit(worker, self.find_nearest_shore(worker))

    def get_unoccupied_gold_mine_coordinates(self):
        coords = []
        indices = []

        for i, gold_mine in enumerate(self._gold_mines):
            if gold_mine.unit is None:
                coords.append([gold_mine.x, gold_mine.y])
                indices.append(i)

        return indices, np.asarray(coords)
    
    def spawn_miner(self):
        if self.can_afford_unit(self._jobs_by_title[str(UnitTypes.WORKER)]):
            if self.select_spawner_for_unit(UnitTypes.WORKER).unit == None:
                tile = self.spawn_unit(UnitTypes.WORKER)
                if tile.unit:
                    self.miners.append(tile.unit)

    def control_miners(self):
        dead_miners = []

        for worker in self.miners:
            if worker.tile is None:
                dead_miners.append(worker)
                continue
            
            if worker.tile.is_gold_mine == True:
                worker.mine(worker.tile)
            if worker.tile.is_gold_mine == False and worker.tile.is_island_gold_mine == False:
                self.move_unit(worker, self.get_closest_gold_mine(worker))
    
        for dead_miner in dead_miners:
            self.miners.remove(dead_miner)
        
    def select_random_attacker_type(self):
        choice = random.choice(list(self._unit_types))
        while choice == UnitTypes.WORKER:
            choice = random.choice(list(self._unit_types))
        return choice
    
    def get_attack_units(self):
        units = []
        for unit in self.player.units:
            if unit.job.title != UnitTypes.WORKER:
                units.append(unit)
        
        return units

    def get_closest_gold_mine(self, unit):
        tile = self.get_tile_from(unit)

        if self.is_gold_mine(tile) or tile is None:
            return tile if tile is not None else unit.tile
        
        coords = np.array([[tile.x, tile.y]])
        indices, gold_mine_coordinates = self.get_unoccupied_gold_mine_coordinates()

        if len(gold_mine_coordinates):
            dist = self.distance_vectorized(coords, gold_mine_coordinates)
        else:
            dist = self.distance_vectorized(coords, self._gold_mine_coordinates)
            return self._gold_mines[np.argmin(dist)]
        
        return self._gold_mines[indices[np.argmin(dist)]]
    
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
        return tile.is_gold_mine or tile.is_island_gold_mine
    
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

    def get_unit_type(self, unit: Unit):
        return self._unit_types[unit.job.title]

    def can_move_unit_to(self, tile: Tile, unit_type: UnitTypes):
        num_unit_on_tile = defaultdict(lambda: tile.unit.job.title == str(unit_type) if tile.unit is not None else 0)
        num_unit_on_tile[UnitTypes.GHOUL] = tile.num_ghouls
        num_unit_on_tile[UnitTypes.HOUND] = tile.num_hounds
        num_unit_on_tile[UnitTypes.ZOMBIE] = tile.num_zombies

        if tile.unit is not None and tile.unit.job.title != str(unit_type):
            return False
        if not (num_unit_on_tile[unit_type] < self._jobs_by_title[str(unit_type)].per_tile):
            return False

        if unit_type is None:
            return True
        if unit_type != UnitTypes.WORKER:
            return tile.is_path
        else:
            return tile.is_grass or tile.is_gold_mine or tile.is_island_gold_mine
        
    def find_path(self, start, goal, f_metric=None):
        f_metric = f_metric if f_metric else self.distance
        unit_type = None

        if isinstance(start, Unit):
            unit_type = self.get_unit_type(start)
        elif isinstance(start, Tile):
            unit_type = start.unit
        
        start = self.get_tile_from(start)
        goal = self.get_tile_from(goal)
        visited = set(start.id)

        came_from = {}
        g_score = defaultdict(lambda: np.inf)
        g_score[start] = 0
        f_score = defaultdict(lambda: np.inf)
        f_score[start] = f_metric(start, goal)
        priority_queue = [(f_score[start], start.id, start)]
        unpathable = 0

        while priority_queue:
            _, tile_id, current_tile = heapq.heappop(priority_queue)

            if current_tile == goal:
                return self._reconstruct_path(current_tile, came_from, start)
            
            unpathable = 0

            for neighbor in current_tile.get_neighbors():
                if neighbor != goal and not self.can_move_unit_to(neighbor, unit_type):
                    unpathable += 1
                    continue
                
                score = g_score[current_tile] + self.move_cost(start, goal)

                if score < g_score[neighbor]:
                    came_from[neighbor] = current_tile
                    g_score[neighbor] = score
                    f_score[neighbor] = g_score[neighbor] + f_metric(current_tile, neighbor)
                    
                    if neighbor not in visited:
                        visited.add(neighbor.id)
                        heapq.heappush(priority_queue, (f_score[neighbor], neighbor.id, neighbor))
            
            if unpathable == len(current_tile.get_neighbors()):
                return self._reconstruct_path(current_tile, came_from, start)
            
        self.logger.warn(f'Failed to find path for unit `{unit_type}`.')
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