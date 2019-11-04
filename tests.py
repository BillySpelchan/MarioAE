# -*- coding: utf-8 -*-
"""
Created on Sat Oct 26 13:39:51 2019

@author: spelc
"""

from mario.level import Level, EnvironmentalSetBuilder, MapManager

LEVELS_IN_SET=[
    "levels/mario-1-1.txt", "levels/mario-1-2.txt", "levels/mario-1-3.txt",
    "levels/mario-2-1.txt",
    "levels/mario-3-1.txt", "levels/mario-3-3.txt",
    "levels/mario-4-1.txt", "levels/mario-4-2.txt",
    "levels/mario-5-1.txt", "levels/mario-5-3.txt",
    "levels/mario-6-1.txt", "levels/mario-6-2.txt", "levels/mario-6-3.txt",
    "levels/mario-7-1.txt",
    "levels/mario-8-1.txt"]


mapman = MapManager()
level = mapman.get_map("levels/mario-1-1.txt")
for col in range(150):
    level.column_to_string(col, True)
    
emap = EnvironmentalSetBuilder(level)
emap.print_bin_level_slice()

sub_map = emap.get_bin_level_slice(50,8)
noisy_map = emap.add_noise_to_slice(sub_map, 0.05)
print ("slice without noise")
emap.print_bin_level_slice(sub_map)
print ("slice with noise")
emap.print_bin_level_slice(noisy_map)

emap.compare_slice_to_col_string(sub_map, noisy_map)
#test_list = mapman.load_and_slice_levels(LEVELS_IN_SET, 4, True, False)
#print ("Test data loaded")

