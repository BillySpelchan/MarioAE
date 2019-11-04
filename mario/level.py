# -*- coding: utf-8 -*-
"""

@author: Billy D. Spelchan
"""
import numpy as np
import random

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

    def add_noise_to_slice(self, slce, noise_rate):
        noisy_slice = np.zeros(slce.shape)
        for indx in range(slce.shape[0]):
            rnd = random.random()
            if rnd < noise_rate:
                if (slce[indx] < 0.5):
                    noisy_slice[indx] = 1.0
                else:
                    noisy_slice[indx] = 0
            else:
                noisy_slice[indx] = slce[indx]
        return noisy_slice


    def bin_level_slice_to_string(self, slc):
        cols = slc.shape[0] // 14
        s = ""
        for x in range (0,cols):
            for y in range (0,14):
                tile = slc[x*14+13-y]
                if (tile > .5):
                    s += 'X'
                else:
                    s += '-'
            s += '\n'
        return s

    def print_bin_level_slice(self, slce = None):
        if slce is None:
            slce = self.get_bin_level_slice(0, self.emap.shape[0])
        s = self.bin_level_slice_to_string(slce)            
        print(s)

    # COMPARISON OF SLICES

    """
        compares slices returning a np byte matrix with 
            0 = both match with empty
            1 = both match with wall
            2 = should be empty but is wall
            3 = should be wall but is empty
    """
    def compare_slices(self, original, derived):
        results = np.zeros(original.shape, dtype=np.int8)
        for indx in range(original.shape[0]):
            originalIsWall = original[indx] > .5
            derivedIsWall = derived[indx] > .5
            if originalIsWall:
                if derivedIsWall:
                    results[indx] = 1
                else:
                    results[indx] = 2
            else:
                if derivedIsWall:
                    results[indx] = 3
                else:
                    results[indx] = 0
        return results
  
    def compare_slice_to_col_string(self, original, derived):
        COMP_LETTERS = "-XOH"
        orig_strs = self.bin_level_slice_to_string(original).split('\n')
        der_strs = self.bin_level_slice_to_string(derived).split('\n')
        comp = self.compare_slices(original, derived)
        indx = 0
        for col in range(len(orig_strs)-1):
            print(orig_strs[col], " | ", der_strs[col], ' | ', end='')
            for row in range(14):
                print(COMP_LETTERS[comp[indx+13-row]], end='')
            indx += 14
            print()
            
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
        
    def load_and_slice_level(self, map_name, num_col_in_slice, overlap_slices, verbose=False):
        level = self.get_map(map_name)
        lvl = level.level_data
        slice_skip =  1 if overlap_slices else num_col_in_slice
        cols = lvl.shape[0]
        emap = EnvironmentalSetBuilder(level)
        slc = emap.get_bin_level_slice(0, num_col_in_slice)
        slices = slc.reshape((1,14*num_col_in_slice))
        if verbose:
            emap.print_bin_level_slice(slices[0])
        slice_col = slice_skip
        while (slice_col + num_col_in_slice) <= cols:
            slc = emap.get_bin_level_slice(slice_col, num_col_in_slice)
            if verbose:
                emap.print_bin_level_slice(slc)
            slices = np.append(slices, slc.reshape((1,14*num_col_in_slice)), axis=0)
            slice_col += slice_skip
        return slices
            
    def load_and_slice_levels(self, level_set, num_col_in_slice, overlap_slices, verbose=False):
        slices = None
        for name in level_set:
            if verbose:
                print("Loading and processing level ", name)
            slc = self.load_and_slice_level(name, num_col_in_slice, overlap_slices, verbose)
            if slices is None:
                slices = slc
            else:
                slices = np.append(slices, slc, axis=0)
        return slices