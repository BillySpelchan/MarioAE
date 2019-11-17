# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 08:27:06 2019

@author: spelc
"""
import random
import numpy as np
from mario.level import Level, EnvironmentalSetBuilder, MapManager
from mario.model import MarioModel

class ColumnPredictor:
    def __init__(self, manager, level_list, verbose=True):
        self.overall_chance_solid = np.zeros((14))
        self.follow_empty_chance_solid = np.zeros((14))
        self.follow_solid_chance_solid = np.zeros((14))
        follow_empty_count = np.zeros((14))
        follow_solid_count = np.zeros((14))
        
        slices = manager.load_and_slice_levels(level_list, 1, False)
        num_cols = slices.shape[0];
        if verbose:
            print("debug column predictor columns ", num_cols)
        prev_slc = slices[0]
        for slc in slices:
            print(slc)
            for row in range(14):
                if slc[row] > .5:
                    follow_solid_count[row] += 1
                    self.overall_chance_solid[row] += 1
                    if prev_slc[row] > .5:
                        self.follow_solid_chance_solid[row] += 1
                    else:
                        self.follow_empty_chance_solid[row] += 1
                else:
                    follow_empty_count[row] += 1
            prev_slc = slc
        
        if verbose:
            print("overall chance solid raw count ", self.overall_chance_solid)
            print("follow empty chance solid raw count ", self.follow_empty_chance_solid)
            print("follow empty count ", follow_empty_count)
            print("follow solid chance solid raw count ", self.follow_solid_chance_solid)
            print("folow solid count ", follow_solid_count)
        for row in range(14):
            self.overall_chance_solid[row] = self.overall_chance_solid[row]/num_cols
            if follow_empty_count[row] > 0:
                self.follow_empty_chance_solid[row] = self.follow_empty_chance_solid[row] / follow_empty_count[row]
            if follow_solid_count[row] > 0:
                self.follow_solid_chance_solid[row] = self.follow_solid_chance_solid[row] / follow_solid_count[row]
        if verbose:
            print("overall chance solid ", self.overall_chance_solid)
            print("follow empty chance solid ", self.follow_empty_chance_solid)
            print("follow solid chance solid ", self.follow_solid_chance_solid)


    def buildSlice(self, prev_slice):
        result = np.empty((14))
        for row in range(14):
            rnd = random.random()
            if prev_slice is None:
                result[row] = 1 if rnd < self.overall_chance_solid[row] else 0
            elif prev_slice[row] > .5:
                result[row] = 1 if rnd < self.follow_solid_chance_solid[row] else 0
            else:
                result[row] = 1 if rnd < self.follow_empty_chance_solid[row] else 0
        return result

    def generate(self, cols, use_prev=False):
        prev = self.buildSlice(None)
        for col in range(cols):
            if (use_prev):
                prev = self.buildSlice(prev)
            else:
                prev = self.buildSlice(None)
            print(prev)
                

class Generator:
    def __init__(self, model):
        self.model = model
        self.emap = EnvironmentalSetBuilder(None)
        
    def generate(self, reference_set, noise = .01, cols=100):
        print(reference_set.shape)
        generated = EnvironmentalSetBuilder(None)
        slc = np.zeros((56))
        for chunk in range(cols//4):
            for i in range(56):
                src = reference_set[random.randrange(reference_set.shape[0])]
                slc[i] = src[i]
            slc = emap.add_noise_to_slice(slc, noise)
            gslc = model.predict_slice(slc)
            emap.compare_slice_to_col_string(slc, gslc[0])
            generated.add_slice_to_map(gslc[0,:])
        return generated

    def rolling_generator(self, reference_set, noise = .01, cols=100):
        slc = np.copy(reference_set[0])
        generated = EnvironmentalSetBuilder(None)
        for chunk in range(cols):
            for i in range(14):
                src = reference_set[random.randrange(reference_set.shape[0])]
                slc[42+i] = src[42+i]
            slc = emap.add_noise_to_slice(slc, noise)
            gslc = model.predict_slice(slc)
            generated.add_slice_to_map(gslc[0,0:14])
            np.roll(slc, 14)
        return generated        


class ValidateMap:
    ACTION_NONE = 0
    ACTION_MOVING = 1
    ACTION_JUMP1 = 2
    ACTION_JUMP2 = 4
    ACTION_JUMP3 = 8
    ACTION_FALLING = 16

    def __init__(self):
        self.todo = True
        #nothing
    
    def build_path_slice(self, emap_slice, prev_emap_slice=None, prev_path_slice=None):
        results = np.zeros((14), dtype=np.int8)
        if prev_emap_slice is None:
            # create a starting path slice
            highest_platform = 0
            for row in range(1,14):
                if emap_slice[row] > .5:
                    highest_platform = row
                    break
            if highest_platform == 0:
                for row in range(13):
                    results[row] = ValidateMap.ACTION_FALLING
            else:
                results[highest_platform-1] = ValidateMap.ACTION_MOVING
        else:
            #proper slice
            freefall = False
            for row in range (13): # bottom row is death so ...
                if emap_slice[row] < .5: # if player can enter tile
                    state = 0
                    if (prev_path_slice[row] & 1) == 1:
                        if emap_slice[row+1] < .5:
                            freefall = True
                    t = prev_path_slice[row+1]
                    if (t & 1) == 1: state = state | 2
                    if (t & 2) == 2: state = state | 4
                    if (t & 4) == 4: state = state | 8
                    if (t & 8) == 8: freefall = True
                    if (row < 12):
                        t= prev_path_slice[row+2]
                        if (t & 1) == 1: state = state | 4
                        if (t & 2) == 2: state = state | 8
                        if (t & 4) == 4: freefall = True
                    if (row < 11):
                        t= prev_path_slice[row+3]
                        if (t & 1) == 1: state = state | 8
                        if (t & 2) == 2: freefall = True
                    if (row < 10):
                        t= prev_path_slice[row+3]
                        if (t & 1) == 1: freefall = True
                    if (row > 0):
                        t= prev_path_slice[row-1]
                        if t>0: freefall = True
                    if (freefall): 
                        if (emap_slice[row+1] > .5):
                            state = state | 1
                            freefall = False
                        else:
                            state = state | 16
                    results[row] = state
        print(results)
        return results

    def check_map(self, emap):
        prev_slice = emap.get_bin_level_slice(1, 1)
        prev_path = self.build_path_slice(prev_slice, None)
        for col in range (1, emap.emap.shape[0]):
            slc = emap.get_bin_level_slice(col, 1)
#            print('*',slc)
            prev_path = self.build_path_slice(slc, prev_slice, prev_path)
            prev_slice = slc
            

if __name__ == "__main__":
    mapman = MapManager()
    level = mapman.get_map("levels/mario-1-1.txt")
    emap = EnvironmentalSetBuilder(level)

    validate = ValidateMap()
    validate.check_map(emap)
    
"""
    test_list = mapman.load_and_slice_levels([
        "levels/mario-1-1.txt", "levels/mario-1-2.txt", "levels/mario-1-3.txt",
        "levels/mario-2-1.txt",
        "levels/mario-3-1.txt", "levels/mario-3-3.txt",
        "levels/mario-4-1.txt", "levels/mario-4-2.txt",
        "levels/mario-5-1.txt", "levels/mario-5-3.txt",
        "levels/mario-6-1.txt", "levels/mario-6-2.txt", "levels/mario-6-3.txt",
        "levels/mario-7-1.txt",
        "levels/mario-8-1.txt"], 4, True, False)
    
    model = MarioModel()
    model.load()
    gen = Generator(model)
    gmap = gen.rolling_generator(test_list, .05)
#    slc.print_bin_level_slice()
    lvl = gmap.convert_to_level()
"""    
   
"""
    cp = ColumnPredictor(mapman, [
        "levels/mario-1-1.txt", "levels/mario-1-2.txt", "levels/mario-1-3.txt",
        "levels/mario-2-1.txt",
        "levels/mario-3-1.txt", "levels/mario-3-3.txt",
        "levels/mario-4-1.txt", "levels/mario-4-2.txt",
        "levels/mario-5-1.txt", "levels/mario-5-3.txt",
        "levels/mario-6-1.txt", "levels/mario-6-2.txt", "levels/mario-6-3.txt",
        "levels/mario-7-1.txt",
        "levels/mario-8-1.txt"])
    print("LEVEL WITHOUT PREV KNOWLEDGE")
    cp.generate(50)
    print("LEVEL WITH PREV KNOWLEDGE")
    cp.generate(50, True)
"""