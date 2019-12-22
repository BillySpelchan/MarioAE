# -*- coding: utf-8 -*-
"""
Created on Sun Dec 22 09:05:32 2019

@author: Billy D. Spelchan
"""

import stparser

def analyse_levels():
    flagged_list = []
    potential_list = []
    f = open ("levels/levellist.txt", 'r')
    for line in f:
        print ("processing: ", line)
        pngname = line.replace('.stl', '.png').rstrip()
        level = stparser.STLevel()
        level.load_level(line.rstrip())
        solid_map = level.get_combined_solid()
        if solid_map is None:
            flagged_list.append(line.rstrip() + " No tilemaps???")
            continue
        print ("resulting map is shape ", solid_map.shape)
        if solid_map.shape[1] != 27:
            flagged_list.append(line.rstrip() + " wrong shape " + str(solid_map.shape))
        else:
            potential_list.append(line.rstrip())
        print ("saving environment image to ", pngname)
        img = stparser.generate_image_from_slice(level.get_slice(0, solid_map.shape[0]))
        img.save(pngname)
        print()
    f.close()
    return (potential_list, flagged_list)
        
    #stparser.generate_image_from_slice(slc)
if __name__ == "__main__":
    p_lst, f_lst = analyse_levels()
    print()
    print("*** flagged files ***")
    for l in f_lst:
        print(l)
    print()
    print("*** Shortlist files ***")
    for l in p_lst:
        print(l)