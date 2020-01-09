# -*- coding: utf-8 -*-
"""
Created on Mon Dec  9 19:41:49 2019

@author: spelc
"""
import numpy as np
from PIL import Image as pimg


class STFormatException(Exception):
    def __init__(self, message):
        self.message = message


class STFileNode:
    def __init__(self, name=""):
        self.node_name = name
        self.parent = None
        self.children = None
        self.prev = None
        self.next = None
        self.payload = None
        
    def print_self_and_children(self, depth=0):
        for d in range(depth):
            print("-", end="")
        print (">", self.node_name)

        # process all children
        sibling = self.children
        while (sibling is not None):
            sibling.print_self_and_children(depth + 1)
            sibling = sibling.next
        
    def add_sibling(self, sibling):
        currently_last_sibling = self
        while (currently_last_sibling.next is not None):
            currently_last_sibling = currently_last_sibling.next
        sibling.prev = currently_last_sibling
        currently_last_sibling.next = sibling

    def add_child(self, child):
        child.parent = self
        if self.children is None:
            self.children = child
        else:
            self.children.add_sibling(child)

    """ finds node and parses content within node. Returns end index of node """
    def parse_from_string(self, s, offset = 0):
        #find '(' to start node
        str_size = len(s)
        indx = offset
        while (s[indx] != '('):
            indx += 1
            if indx > str_size:
                raise STFormatException("Unable to find start of node")
        nodename = ""
        indx += 1
        while (s[indx].isspace() == False and s[indx]!='(' and s[indx]!=')'):
            nodename += s[indx]
            indx +=1
        #print ("debug..adding node ", nodename)
        self.node_name = nodename
        payload = ""
        while (s[indx] != ")"):
            if (s[indx] == '('):
                child = STFileNode()
                indx = child.parse_from_string(s, indx)
                self.add_child(child)
            else:
                payload += s[indx]
                indx += 1
        self.payload = payload
        return indx+1

    def get_list_of_nodes_of_type(self, node_type):
        nodes = []
        sibling = self
        while (sibling is not None):
            if sibling.node_name == node_type:
                nodes.append(sibling)
            if sibling.children is not None:
                nodes = nodes + sibling.children.get_list_of_nodes_of_type(node_type)
            sibling = sibling.next
        return nodes
    
    def get_child_by_name(self, child_name):
        child = None
        candidate = self.children
        while candidate is not None:
            if candidate.node_name == child_name:
                child = candidate
                candidate = None
            else:
                candidate = candidate.next
        return child

    def parse_float_from_child(self, childname, default):
        child = self.get_child_by_name(childname)
        if child is None:
            return default
        try:
            val = float(child.payload)
        except Exception:
            val = default
        return val


class STTilemap:
    def __init__(self, tilemap_node = None):
        self.source_node = tilemap_node
        self.width = 0
        self.height = 0
        self.tiles = None
        self.is_solid = True
        self.speed_x = 1.0
        self.speed_y = 1.0
        self.zpos = 0
        self.name = "unnamed"
        if tilemap_node is not None:
            self.set_from_tilemap_node(tilemap_node)
        


    def parse_float_from_node(self, node, childname, default):
        child = node.get_child_by_name(childname)
        if child is None:
            return default
        try:
            val = float(child.payload)
        except Exception:
            val = default
        return val
    
    
    def set_from_tilemap_node(self, node):
        solid = node.get_child_by_name("solid")
        #print("debug - solid payload:", solid.payload)
        self.is_solid = False if 'f' in solid.payload else True
        
        self.speed_x = self.parse_float_from_node(node, "speed-x", 1.0)
        self.speed_y = self.parse_float_from_node(node, "speed-y", 1.0)
        self.zpos = self.parse_float_from_node(node, "z-pos", 0)
        self.width = self.parse_float_from_node(node, "width", 1)
        self.height = self.parse_float_from_node(node, "height", 1)
        self.name = node.get_child_by_name("name")
        if (self.name is None):
            self.name = "unnamed"
        tiles = node.get_child_by_name("tiles").payload.split(' ')
        # have to manually go through payload to avoid non-numeric tiles
        # as spacing is not even
        self.tiles = np.zeros((int(self.width), int(self.height)))
        col = 0
        row = 0
        for t in tiles:
            try:
                n = int(t)
                self.tiles[col,row] = n
                col += 1
                if col >= self.width:
                    col = 0
                    row += 1
            except:
                pass
        #print("debug ", self.width, ",", self.height, " ? ", row, ",", col )
        

class STLevel:
    def __init__(self, filename=None):
        self.raw_level = None
        self.root = None
        self.tilemaps = []
        if (filename is not None): self.load_level(filename)
        self.combined_solid = None

        
    def load_level(self, filename):
        f = open(filename, 'rt')
        self.raw_level = f.read()
        f.close()
        self.root = STFileNode()
        self.root.parse_from_string(self.raw_level)
        self.tilemaps = []
        maps = self.root.get_list_of_nodes_of_type("tilemap")
        for tm in maps:
            self.tilemaps.append(STTilemap(tm))
        self.combined_solid = None
            
    def get_combined_solid(self):
        if self.combined_solid is not None:
            return self.combined_solid
        shortlist = []
        w = 0
        h = 0
        for tm in self.tilemaps:
            if tm.is_solid:
                shortlist.append(tm)
                #print("debug adding ", tm.name)
                if (w < tm.width): w = tm.width
                if (h < tm.height): h = tm.height

        if (w == 0) or (h == 0):
            return None
        combined = np.zeros((int(w), int(h)))
        for tm in shortlist:
            for c in range(int(tm.width)):
                for r in range(int(tm.height)):
                    if (tm.tiles[c,r] > 0):
                        combined[c,r] = tm.tiles[c,r]
        return combined

    def get_slice(self, start_col, num_cols):
        solid = self.get_combined_solid()
        slc = np.zeros((num_cols, solid.shape[1]))
        for c in range(num_cols):
            for r in range(solid.shape[1]):
                slc[c,r] = 1. if solid[c+start_col, r] > 0 else 0
        return slc
 
    def get_starting_location(self):
        spawnpoints = self.root.get_list_of_nodes_of_type("spawnpoint")
        loc = (0,0)
        for spawnpoint in spawnpoints:
            name = spawnpoint.get_child_by_name("name")
            if name is not None:
                if ("\"main\"" in name.payload ):
                    x_pixel = spawnpoint.parse_float_from_child("x", 0)
                    y_pixel = spawnpoint.parse_float_from_child("y", 0)
                    loc = (x_pixel//32, y_pixel//32)
        return loc
            
class MapManager:
    def __init__(self):
        self.maps = {}
        self.enironment_maps = {}
        
    def get_map(self, map_name):
        if map_name in self.maps:
            return self.maps[map_name]
        else:
            newmap = STLevel()
            newmap.load_level(map_name)
            self.maps[map_name] = newmap
            return newmap
    
    def add_map(self, map_name, level):
        self.maps[map_name] = level
        

# ***************************************************
        
# TODO - Move to separte test module once stablized

def generate_image_from_slice(slc):
    img = pimg.new('RGBA', slc.shape)
    for c in range(slc.shape[0]):
        for r in range(slc.shape[1]):
            if (slc[c,r] == 0):
                img.putpixel((c,r), (0,0,0,255))
            else:
                img.putpixel((c,r), (255,0,255,255))
    return img

def test_stfilenode():
    root = STFileNode("1")
    branch = STFileNode("1-1")
    branch.add_child(STFileNode("1-1-1"))
    branch.add_child(STFileNode("1-1-2"))
    branch.add_child(STFileNode("1-1-3"))
    root.add_child(branch)
    branch = STFileNode("1-2")
    branch.add_child(STFileNode("1-2-1"))
    branch.add_child(STFileNode("1-2-2"))
    branch.add_child(STFileNode("1-2-3"))
    root.add_child(branch)
    root.print_self_and_children()            

    parseroot = STFileNode()
    parseroot.parse_from_string("(2 (2-1 (2-1-1)(2-1-2)(2-1-3))(2-2(2-2-1)(2-2-2)(2-2-3)))")
    parseroot.print_self_and_children()  

def test_sttilemap():
    f = open("tuxlevels/icy_valley.stl", 'rt')
    s = f.read()
    f.close()
    root = STFileNode()
    root.parse_from_string(s)
    root.print_self_and_children()
    tilemaps = root.get_list_of_nodes_of_type("tilemap")
    print("there are ", len(tilemaps), " tile maps in the file.")
    print(tilemaps[0].get_child_by_name("tiles").payload)
    tm = STTilemap(tilemaps[0])
    print (tm.tiles)
    

def test_stlevel(mm):
    level = mm.get_map("levels/icy_valley.stl")
    solid_map = level.get_combined_solid()
    print(solid_map)
    img = generate_image_from_slice(level.get_slice(0, 512))
    img.save("test.png")
    return solid_map

if __name__ == "__main__":
#    test_stfilenode()
#    test_sttilemap()
    mm = MapManager()
#    sm = test_stlevel(mm)
    level = mm.get_map("levels/bonus1/abednego-level1.stl")
    level.get_starting_location()
    
