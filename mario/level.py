# -*- coding: utf-8 -*-
"""

@author: Billy D. Spelchan
"""
import numpy as np

class Level:
    TILE_EMPTY = 0
    TILE_COIN = 1
    TILE_ENEMY = 2
    TILE_BREAKABLE = 3
    TILE_QUESTION = 4
    TILE_POWERUP = 5
    TILE_LEFT_PIPE = 6
    TILE_RIGHT_PIPE = 7
    TILE_LEFT_PIPE_TOP = 8
    TILE_RIGHT_PIPE_TOP = 9
    TILE_LEFT_BULLET_BILL = 10
    TILE_RIGHT_BULLET_BILL = 11
    TILE_BRICK = 12
    PATH_TILES = "-oES?Q<>[]bBX*@"
    
    def __init__(self):
        print("Init tileset ", Level.PATH_TILES)
        self.level_name = None
        self.level_data = None
        self.num_cols = 0

    def load_level(self, level_name):
        f = open(level_name, "r")
        raw_level = f.readlines()
        f.close()

        self.num_cols = len(raw_level[0])-1
    
        self.level_data = np.zeros((self.num_cols, 14))
        for col in range(0, self.num_cols) :
            for row in range(0,14) :
                tile = Level.PATH_TILES.index(raw_level[row][col])
                #todo error correction for invalid tiles
                self.level_data[col][row] = tile
        return self.level_data
        
    def column_to_string(self, column, verbose=False):
        s = ""
        for y in range (0,14):
            tile = self.level_data[column, 13-y]
            s += Level.PATH_TILES[int(tile)]
        if verbose:
            print(s)
        return s
        