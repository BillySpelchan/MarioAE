# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 08:27:06 2019

@author: spelc
"""
import random
import numpy as np
from mario.level import Level, EnvironmentalSetBuilder, MapManager
from mario.model import MarioModel


class Generator:
    def __init__(self, model):
        self.model = model
        self.emap = EnvironmentalSetBuilder(None)
        
    def generate(self, reference_set, noise = .01, cols=100):
        print(reference_set.shape)
        slc = np.zeros((56))
        for chunk in range(cols//4):
            for i in range(56):
                src = reference_set[random.randrange(reference_set.shape[0])]
                slc[i] = src[i]
            slc = emap.add_noise_to_slice(slc, noise)
            gslc = model.predict_slice(slc)
            emap.compare_slice_to_col_string(slc, gslc[0])
        
        return slc


if __name__ == "__main__":
    mapman = MapManager()
    level = mapman.get_map("levels/broken.txt")
    emap = EnvironmentalSetBuilder(level)

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
    slc = gen.generate(test_list, .025)
    emap.print_bin_level_slice(slc)
