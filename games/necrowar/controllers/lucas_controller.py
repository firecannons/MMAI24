import logging
from ..game import Game
from ..player import Player
from .central_command import BaseController, UnitTypes
import random

class LucasController(BaseController):
    def __init__(self, logger: logging.Logger, game: Game, player: Player):
        super().__init__(logger, game, player)
        self.numbers = []
        self.numbers.append(random.random()) # prob of spawn miner
        self.numbers.append(random.random()) # prob of spawn fisher
        self.numbers.append(random.random()) # prob of spawn attacker
        self.numbers.append(random.random()) # prob of spawn tower

        self.numbers.append(random.random()) # prob of spawn Worker
        self.numbers.append(random.random()) # prob of spawn Zombie
        self.numbers.append(random.random()) # prob of spawn Ghoul
        self.numbers.append(random.random()) # prob of spawn Abomination
        self.numbers.append(random.random()) # prob of spawn Hound
        self.numbers.append(random.random()) # prob of spawn Wraith
        self.numbers.append(random.random()) # prob of spawn Horseman
        
        self.numbers.append(random.random()) # prob of spawn Arrow
        self.numbers.append(random.random()) # prob of spawn Ballista
        self.numbers.append(random.random()) # prob of spawn Cleansing
        self.numbers.append(random.random()) # prob of spawn Aoe

        print(self.numbers)
    
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
        self.spawn_builder()
        if random.random() < self.numbers[0]:
            self.spawn_miner()
        if random.random() < self.numbers[1]:
            self.spawn_fisher()
        self.control_miners()
        self.control_fishers()
        self.control_builders()
        if random.random() < self.numbers[2]:
            self.spawn_attackers()
        if random.random() < self.numbers[3]:
            self.build_tower()
        self.move_attackers()
        self.attackers_attack()
        self.towers_attack()
        self.enemy_health = self.enemy_castle.tower.health
        self.turn = self.game.current_turn
        self.logger.info(f'Hello from Lucas!')
    
    def end_game(self):
        result = ''
        if self.enemy_health <= 0:
            result = 'won'
        else:
            result = 'lost'
        with open("data.txt", "a") as myfile:
            myfile.write(result + ' ' + str(self.numbers) + ' ' + self.game.session + ' ' + str(self.turn) + ' ' + self.player.reason_lost + ' ' + self.player.reason_won + '\n')
            myfile.close()