# -*- coding: utf-8 -*-
"""
Created on Sun Dec 22 09:05:32 2019

@author: Billy D. Spelchan
"""

import stparser
import json

def group_levels_by_size(json_output = None, verbose=False):
    groupings = {}
    f = open ("levels/levellist.txt", 'r')
    for line in f:
        level = stparser.STLevel()
        sline = line.rstrip()
        if (verbose):
            print("Processing file: ", sline)
        level.load_level(sline)
        solid_map = level.get_combined_solid()
        if solid_map is None:
            continue
        key = str(solid_map.shape[1])
        if key not in groupings:
            groupings[key] = []
        groupings[key].append(sline)            
    f.close()
    if json_output is not None:
        j = json.dumps(groupings)
        f = open(json_output, 'w')
        f.write(j)
        f.close()
    return groupings
    
def make_png_of_all_levels():
    f = open ("levels/levellist.txt", 'r')
    for line in f:
        pngname = line.replace('.stl', '.png').rstrip()
        level = stparser.STLevel()
        level.load_level(line.rstrip())
        solid_map = level.get_combined_solid()
        if solid_map is None:
            continue
        print ("saving environment image to ", pngname)
        img = stparser.generate_image_from_slice(level.get_slice(0, solid_map.shape[0]))
        img.save(pngname)
    f.close()
        

if __name__ == "__main__":
    #groupings = group_levels_by_size("levellist.json", True)
    f = open("levellist.json", 'r')
    s = f.read()
    f.close()
    j = json.loads(s)
    f = open("level_count.csv", 'w' )
    for k in j.keys():
        f.write(k)
        w = len(j[k])
        f.write(',')
        f.write(str(w))
        f.write('\n')
        print(k, " has " , w, " levels")
    f.close()
 