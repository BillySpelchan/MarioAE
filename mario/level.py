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


class MapManager:
    def __init__(self):
        self.maps = {}
        self.enironment_maps = {}
        
    def get_map(self, map_name):
        if map_name in self.maps:
            return self.maps[map_name]
        else:
            newmap = Level()
            newmap.load_level(map_name)
            self.maps[map_name] = newmap
            return newmap
    
    def add_map(self, map_name, level):
        self.maps[map_name] = level

class EnvironmentalSetBuilder:
    TILE_2_BIN = [0.,0.,1.,1.,1.,1.,1.,1.,1.,1.,1.,1.,1.,0.,0.]

    def __init__(self, level) :
        self.source = level
        self.emap = np.zeros(level.level_data.shape)
        self.refresh_map()

    def refresh_map(self):
        level = self.source
        if (self.emap.shape[0] != level.num_cols) :
            self.emap = np.zeros(level.level_data.shape)
        for col in range(0, level.num_cols):
            for row in range(0, 14):
                self.emap[col][row] = EnvironmentalSetBuilder.TILE_2_BIN[
                        int(level.level_data[col][row])]

    def get_bin_level_slice(self, col, num_cols):
        slce = np.zeros((14*num_cols))
        indx = 0
        for x in range(col, col+num_cols):
            for y in range(0,14):
                tile = int(self.emap[x,y])
                slce[indx] = tile
                indx += 1
        return slce

    def print_bin_level_slice(self, slce = None):
        if slce is None:
            slce = self.get_bin_level_slice(0, self.emap.shape[0])
        cols = slce.shape[0] // 14
        for x in range (0,cols):
            for y in range (0,14):
                tile = slce[x*14+13-y]
                if (tile > .5):
                    print('X', end='')
                else:
                    print('-', end='')
            print()
    
        