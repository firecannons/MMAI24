import logging
from ..game import Game
from ..player import Player
from .central_command import BaseController, UnitTypes
import random

class LucasController(BaseController):
    def __init__(self, logger: logging.Logger, game: Game, player: Player):
        super().__init__(logger, game, player)
    
    def spawn_attackers(self):
        random_type = self.select_random_attacker_type()
        if self.can_afford_unit(self._jobs_by_title[random_type]) == True:
            self.spawn_unit(random_type)
    
    def move_attackers(self):
        for unit in self.get_attack_units():
            self.move_unit(unit, self.enemy_castle)
    
    def attackers_attack(self):
        for unit in self.get_attack_units():
            for tile in unit.tile.get_neighbors():
                if tile.tower != None:
                    if tile.tower.owner != self.player and unit.acted == False:
                        unit.attack(tile)
                if tile.unit != None:
                    if tile.unit.owner != self.player and unit.acted == False:
                        unit.attack(tile)

    def run_turn(self):
        self.spawn_builder()
        self.control_builders()
        self.control_miners()
        self.control_fishers()
        while self.can_afford_unit(self._jobs_by_title[str(UnitTypes.WORKER)]) and len(self.miners) < 7 and self.select_spawner_for_unit(UnitTypes.WORKER).unit == None:
            self.spawn_miner()
            self.control_miners()
        self.control_miners()
        while self.can_afford_unit(self._jobs_by_title[str(UnitTypes.WORKER)]) and len(self.fishers) < 5 and self.select_spawner_for_unit(UnitTypes.WORKER).unit == None:
            self.spawn_fisher()
            self.control_fishers()
        self.control_fishers()
        self.build_tower()
        while random.randint(0, 4):
            self.spawn_attackers()
            self.move_attackers()
            self.attackers_attack()
        self.towers_attack()
        self.enemy_health = self.enemy_castle.tower.health
        self.turn = self.game.current_turn
        self.logger.info(f'Hello from Lucas!')
    
    def end_game(self):
        pass