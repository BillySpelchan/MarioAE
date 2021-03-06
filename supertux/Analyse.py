# -*- coding: utf-8 -*-
"""
Created on Sun Dec 22 09:05:32 2019

@author: Billy D. Spelchan
"""

import stparser
import STEvaluator
import json

def group_levels_by_size(json_output = None, verbose=False):
    """
    Simple utility routine used to generate the levellist.json file that holds
    information about levels and their size. While only needed for one-time
    use I am keeping this here for completeness and if 
    """
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

        
def make_level_count_csv():
    """ 
    Utility method to provide a csv file that outlines how many levels 
    there are for each size of map. Only needed to run once but keeping for
    completeness.
    """
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


def build_path_text_file(filename, lvl_list, only_solvable=False):
    f = open(filename, 'w')
    for lvl in lvl_list:
        f.write('\n\n***** ')
        f.write(lvl)
        print("processing ", lvl, end='')
        f.write(' *****\n\n')
        level = stparser.STLevel()
        level.load_level(lvl)
        loc = level.get_starting_location()
        solid_map = level.get_combined_solid()
        controller = STEvaluator.STMapSliceController(solid_map)
        pf = STEvaluator.STAStarPath(controller, int(loc[0]), int(loc[1]))
        furthest = pf.find_furthest_path_node()
        path = pf.get_path_from_node(furthest)
        s = controller.get_map_as_vertical_string(path)
        solvable = controller.has_won(furthest.x, furthest.y)
        if solvable or not only_solvable:
            f.write(s)
        else:
            f.write("Not solvable!\n\n")
        msg = " Solvable" if solvable else " Not solvable!"
        print(msg)
    f.close()

if __name__ == "__main__":
    #groupings = group_levels_by_size("levellist.json", True)
    f = open("levellist.json", 'r')
    s = f.read()
    f.close()
    j = json.loads(s)
    
    build_path_text_file("temp.txt", j["36"], True)
         
