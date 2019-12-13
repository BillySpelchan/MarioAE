# -*- coding: utf-8 -*-
"""
Created on Mon Dec  9 19:41:49 2019

@author: spelc
"""

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
        print ("debug..adding node ", nodename)
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
        print("debug - solid payload:", solid.payload)
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
        print("debug ", self.width, ",", self.height, " ? ", row, ",", col )
        
        
        
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

            
# TODO - Move to separte test module once stablized
if __name__ == "__main__":
    test_stfilenode()
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
    
