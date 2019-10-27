# -*- coding: utf-8 -*-
"""
Created on Sat Oct 26 13:39:51 2019

@author: spelc
"""

from mario.level import Level, EnvironmentalSetBuilder

level = Level()
level.load_level("levels/mario-1-1.txt")
for col in range(150):
    level.column_to_string(col, True)
    
emap = EnvironmentalSetBuilder(level)
emap.print_bin_level_slice()
