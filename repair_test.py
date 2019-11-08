# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 16:45:59 2019

@author: spelc
"""

from mario.level import Level, EnvironmentalSetBuilder, MapManager
from mario.model import MarioModel

mapman = MapManager()
level = mapman.get_map("levels/broken.txt")
emap = EnvironmentalSetBuilder(level)


test_list = mapman.load_and_slice_levels(["levels/broken.txt"], 4, True, False)

model = MarioModel()
model.load()
for i in range(15):
    prediction = model.predict_slice(test_list[i*4])
    emap.compare_slice_to_col_string(test_list[i*4], prediction[0])

