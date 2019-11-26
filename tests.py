# -*- coding: utf-8 -*-
"""
Created on Sat Oct 26 13:39:51 2019

@author: spelc
"""

from mario.level import Level, EnvironmentalSetBuilder, MapManager
from mario.model import MarioModel

LEVELS_IN_SET=[
    #"levels/mario-1-1.txt", 
    "levels/mario-1-2.txt", "levels/mario-1-3.txt",
    "levels/mario-2-1.txt",
    "levels/mario-3-1.txt", "levels/mario-3-3.txt",
    "levels/mario-4-1.txt", "levels/mario-4-2.txt",
    "levels/mario-5-1.txt", "levels/mario-5-3.txt",
    "levels/mario-6-1.txt", 
    "levels/mario-6-2.txt", "levels/mario-6-3.txt",
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


# model testing
test_list = mapman.load_and_slice_levels(LEVELS_IN_SET, 4, True, False)
print ("Test data loaded")

model = MarioModel()
#model.load()
model.train_model(test_list, 100)
total_err = 0
predict_test = mapman.load_and_slice_levels(["levels/mario-1-1.txt"], 4, True, False)
for i in range(predict_test.shape[0]//4):
    """
    prediction = model.predict_slice(test_list[i*4+50])
    cslc = emap.compare_slices(test_list[i*4+50], prediction[0])
    emap.compare_slice_to_col_string(test_list[i*4+50], prediction[0])
    """
    prediction = model.predict_slice(predict_test[i*4])
    cslc = emap.compare_slices(predict_test[i*4], prediction[0])
    emap.compare_slice_to_col_string(predict_test[i*4], prediction[0])
    col_err = 0
    for row in range(56):
        if (cslc[row] > 1):
            col_err += 1
    print(col_err)
    total_err += col_err
print ("errors: ", total_err, "out of ", (predict_test.shape[0]*14))
        
#model.save()