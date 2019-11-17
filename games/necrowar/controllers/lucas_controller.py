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
                    if tile.tower.owner != self.player:
                        unit.attack(tile)
                if tile.unit != None:
                    if tile.unit.owner != self.player:
                        unit.attack(tile)

    def run_turn(self):
        while self.can_afford_unit(self._jobs_by_title[str(UnitTypes.WORKER)]):
            self.spawn_builder()
            self.spawn_miner()
            self.spawn_fisher()
            self.control_miners()
            self.control_fishers()
            self.control_builders()
            self.spawn_attackers()
        self.control_miners()
        self.control_fishers()
        self.control_builders()
        self.spawn_attackers()
        self.build_tower()
        self.move_attackers()
        self.attackers_attack()
        self.towers_attack()
        self.enemy_health = self.enemy_castle.tower.health
        self.turn = self.game.current_turn
        self.logger.info(f'Hello from Lucas!')
    
    def end_game(self):
        pass