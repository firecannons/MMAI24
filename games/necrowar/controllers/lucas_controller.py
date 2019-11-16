import logging
from ..game import Game
from ..player import Player
from .central_command import BaseController

DRAW = True

if DRAW == True:

    import pygame
    import math

    MAP_WIDTH = 63
    MAP_HEIGHT = 32
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 700
    Game = None
    PATH_COLOR = ( 200 , 200 , 100 )
    GRASS_COLOR = ( 50 , 200 , 50 )
    TOWER_COLOR = ( 200 , 100 , 100 )
    GOLD_COLOR = ( 200 , 255 , 0 )
    WATER_COLOR = ( 0, 0, 255 )
    CASTLE_COLOR = ( 50 , 50 , 50 )
    WORKER_SPAWN_COLOR = ( 0 , 255 , 255 )
    UNIT_SPAWN_COLOR = ( 255, 255, 0 )
    RED_UNIT_COLOR = ( 255 , 0 , 0 )
    BLUE_UNIT_COLOR = ( 0 , 0 , 255 )

    pygame . init ( )
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

def draw(game):
    global Game
    Game = game
    if DRAW == True:
        draw_map()

def getGame():
    global Game
    return Game

def draw_map():
    TileDimension = float(WINDOW_WIDTH) / MAP_WIDTH
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            TileColor = PATH_COLOR
            if getGame().tiles[x + y * MAP_WIDTH].is_river == True:
                TileColor = WATER_COLOR
            if getGame().tiles[x + y * MAP_WIDTH].is_path == True:
                TileColor = PATH_COLOR
            if getGame().tiles[x + y * MAP_WIDTH].is_grass == True:
                TileColor = GRASS_COLOR
            if getGame().tiles[x + y * MAP_WIDTH].is_tower == True:
                TileColor = GRASS_COLOR
            if getGame().tiles[x + y * MAP_WIDTH].is_gold_mine == True or getGame().tiles[x + y * MAP_WIDTH].is_island_gold_mine == True:
                TileColor = GOLD_COLOR
            if getGame().tiles[x + y * MAP_WIDTH].is_castle == True:
                TileColor = CASTLE_COLOR
            if getGame().tiles[x + y * MAP_WIDTH].is_worker_spawn == True:
                TileColor = WORKER_SPAWN_COLOR
            if getGame().tiles[x + y * MAP_WIDTH].is_unit_spawn == True:
                TileColor = UNIT_SPAWN_COLOR
            if getGame().tiles[x + y * MAP_WIDTH].unit != None:
                if getGame().tiles[x + y * MAP_WIDTH].unit.owner == getPlayer():
                    TileColor = BLUE_UNIT_COLOR
                else:
                    TileColor = RED_UNIT_COLOR
            TileRect = pygame.Rect(TileDimension * x, TileDimension * y, TileDimension * x + TileDimension, TileDimension * y + TileDimension)
            pygame.draw.rect(screen, TileColor, TileRect)
    pygame.display.flip()

class LucasController(BaseController):
    def __init__(self, logger: logging.Logger, game: Game, player: Player):
        super().__init__(logger, game, player)

    def run_turn(self):
        draw(self._game)
        self.logger.info(f'Hello from Lucas!')