# -*- coding: utf-8 -*-
"""
Created on Fri Dec 27 15:27:15 2019

@author: Billy D. Spelchan
"""

import unittest
import numpy as np
import STEvaluator

# remember that we use c,r for maps
MAP_WALKING = [[0,0,0,0,0,0,1],[0,0,0,0,0,0,1],[0,0,0,0,0,0,1],
               [0,0,0,0,0,0,1],[0,0,0,0,0,0,1],[0,0,0,0,0,0,1],
               [0,0,0,0,0,0,1] ]

COMPLEX_PATH = [ [0,0,0,0,0,0,1],[0,0,0,0,0,0,1],[0,0,0,0,0,0,1],
                [0,0,0,0,0,0,1],[1,0,0,0,0,0,1],[1,0,0,1,0,0,0],
                [1,0,0,1,0,0,0],[1,0,0,1,0,0,0],[1,0,0,1,0,0,0],
                [1,0,0,0,0,0,0],[1,0,0,0,0,0,0],[1,0,0,0,0,0,0],
                [1,0,0,0,0,0,0],[1,0,0,0,0,0,0],[1,0,0,0,0,0,0],
                [0,0,0,0,0,0,1],[0,0,0,0,0,0,1],[0,0,0,0,0,0,1],
                [0,0,0,0,0,0,1] ]

COMPLEX_PATH_MAP_STRINGS = ["X......","X......","X......",
                            "X......","X.....X","...X..X",
                            "...X..X","...X..X","...X..X",
                            "......X","......X","......X",
                            "......X","......X","......X",
                            "X......","X......","X......",
                            "X......"    ]


class MochMapController:
    def __init__(self, size = 100):
        self.enter_list = []
        self.enter_ranges = []
        self.size = size
    
    def set_enterable_list(self, lst):
        self.enter_list = lst
    
    def add_rectangle(self,x,y,w,h):
        rect = (x,y,w,h)
        self.enter_ranges.append(rect)
        
    def can_enter(self, x, y):
        result = False
        # test specific tiles
        for loc in self.enter_list:
            if (loc[0] == x) and (loc[1] == y):
                result = True
                break
        # test blocks of tiles
        for rect in self.enter_ranges:
            x1 = rect[0]
            x2 = x1 + rect[2]
            y1 = rect[1]
            y2 = x1 + rect[3]            
            if ((x >= x1) and (x < x2)) and ((y >= y1) and (y < y2)):
                result = True
                break
        return result

    def get_num_columns(self):
        return self.size
    
    
class TestMochMapController(unittest.TestCase):
    def test_moch_map_controller(self):
        mmc = MochMapController()
        mmc.set_enterable_list([(1,2), (2,1)])
        self.assertEqual(mmc.can_enter(1,2), True)
        self.assertEqual(mmc.can_enter(2,1), True)
        self.assertEqual(mmc.can_enter(2,2), False)

    def test_adding_rects(self):
        mmc = MochMapController()
        mmc.add_rectangle(5,5,5,5)
        for x in range (5,10):
            for y in range (5,10):
                self.assertEqual(mmc.can_enter(x,y), True)
        for cntr in range (4,11):
            self.assertEqual(mmc.can_enter(4,cntr), False)
            self.assertEqual(mmc.can_enter(10,cntr), False)
            self.assertEqual(mmc.can_enter(cntr,4), False)
            self.assertEqual(mmc.can_enter(cntr,10), False)
            

class TestSTANode(unittest.TestCase):
    def test_generate_forward_node(self):
        # set up moch controller to 
        mmc = MochMapController()
        mmc.set_enterable_list([(11,10), (12,10), (13,10), (14,10), (15,10)])
        node = STEvaluator.STANode(None)
        node.setLocation(10,10, False)
        for step in range(1,5):
            node = node.generate_forward_node(mmc)
            self.assertEqual(node.y, 10)
            self.assertEqual(node.x, 10+step)
            self.assertEqual(node.move_speed, min(step, 3))

    def test_generate_forward_node_when_hitting_something(self):
        # set up moch controller to 
        mmc = MochMapController()
        mmc.set_enterable_list([(11,10), (12,10), (13,10)] )
        node = STEvaluator.STANode(None)
        node.setLocation(10,10, False)
        for step in range(1,4):
            node = node.generate_forward_node(mmc)
            self.assertEqual(node.y, 10)
            self.assertEqual(node.x, 10+step)
            self.assertEqual(node.move_speed, step)
        node = node.generate_forward_node(mmc)
        self.assertEqual(node.x, 13)
        self.assertEqual(node.move_speed, 0)
        node = node.generate_forward_node(mmc)
        self.assertIsNone(node)
    
    def test_freefall_when_invalid(self):
        mmc = MochMapController()
        node = STEvaluator.STANode(None)
        node.setLocation(10,10, False)
        child = node.generate_freefall_node(mmc)
        self.assertIsNone(child)
        node.jump_state = 5
        child = node.generate_freefall_node(mmc)
        self.assertIsNone(child)
        
    def test_freefalling_down(self):
        mmc = MochMapController()
        mmc.set_enterable_list([(10,11), (10,12), (10,13)] )
        node = STEvaluator.STANode(None)
        node.setLocation(10,10, True)
        for step in range(1, 4):
            node = node.generate_freefall_node(mmc)
            self.assertEqual(node.y, 10+step)
            self.assertEqual(node.x, 10)
        # now should be on ground so ...
        self.assertEqual(node.jump_state, 0)
        node = node.generate_freefall_node(mmc)
        self.assertIsNone(node)


    def test_freefall_angle(self):
        mmc = MochMapController()
        mmc.set_enterable_list([(10,11),(10,12),(11,11), (11,12),(11,13),(12,12), (12,13),(12,14),(13,13)] )
        node = STEvaluator.STANode(None)
        node.setLocation(10,10, True)
        for step in range(1, 4):
            node = node.generate_freefall_angle_node(mmc)

            self.assertEqual(node.y, 10+step)
            self.assertEqual(node.x, 10+step)
        # now should be on ground so ...
        self.assertEqual(node.jump_state, 0)
        node = node.generate_freefall_node(mmc)
        self.assertIsNone(node)
        
        
    def test_jumping_up(self):
        mmc = MochMapController()
        mmc.set_enterable_list([(10,9), (10,8), (10,7), (10,6), (10,5)] )
        
        node = STEvaluator.STANode(None)
        node.setLocation(10,10, False)
        for step in range(1, 6):
            node = node.generate_jump_node(mmc)
            self.assertEqual(node.y, 10-step)
            self.assertEqual(node.x, 10)
        # now should be in freefall so ...
        node = node.generate_jump_node(mmc)
        self.assertEqual(node.jump_state, -1)
        self.assertEqual(node.y, 5)
        self.assertEqual(node.x, 10)
        
        node = node.generate_jump_node(mmc)
        self.assertIsNone(node)

    def test_jumping_angle(self):
        mmc = MochMapController()
        mmc.set_enterable_list([(10,9),(11,9), (11,8),(12,8), (12,7),(13,7), (13,6),(14,6), (14,5),(15,5),(15,6)] )
        
        node = STEvaluator.STANode(None)
        node.setLocation(10,10, False)
        for step in range(1, 6):
            node = node.generate_jump_angle_node(mmc)
            self.assertEqual(node.y, 10-step)
            self.assertEqual(node.x, 10+step)
        # now should be in freefall so ...
        node = node.generate_jump_node(mmc)
        self.assertEqual(node.jump_state, -1)
        self.assertEqual(node.y, 5)
        self.assertEqual(node.x, 15)
        
        node = node.generate_jump_node(mmc)
        self.assertIsNone(node)

    def test_different_speed_jumping(self):
        mmc = MochMapController()
        mmc.add_rectangle(10,0, 1,11)
        expected_y = [5,5,4,3]
        for speed in range(0, 4):
            node = STEvaluator.STANode(None)
            node.setLocation(10,10,False)
            node.move_speed = speed
            while not node.is_falling():
                node = node.generate_jump_node(mmc)
            self.assertEqual(node.y, expected_y[speed], "test for speed " + str(speed))
            
    def test_different_speed_jumping_at_angle(self):
        mmc = MochMapController()
        mmc.add_rectangle(10,0, 10,11)
        expected_y = [5,5,4,3]
        expected_x = [16,16,17,18]
        for speed in range(0, 4):
            node = STEvaluator.STANode(None)
            node.setLocation(10,10,False)
            node.move_speed = speed
            while not node.is_falling():
                node = node.generate_jump_angle_node(mmc)
            self.assertEqual(node.y, expected_y[speed], "test for speed y " + str(speed))
            self.assertEqual(node.x, expected_x[speed], "test for speed x " + str(speed))
            
 
    def test_jump_and_bump(self):
        mmc = MochMapController()
        mmc.add_rectangle(10,7, 1,4)
        for speed in range(0, 4):
            node = STEvaluator.STANode(None)
            node.setLocation(10,10,False)
            node.move_speed = speed
            while not node.is_falling():
                node = node.generate_jump_node(mmc)
            self.assertEqual(node.y, 7, "test for bump " + str(speed))

        
    def test_jump_at_angle_and_bump(self):
        mmc = MochMapController()
        mmc.add_rectangle(10,7, 6,4)
        for speed in range(0, 4):
            node = STEvaluator.STANode(None)
            node.setLocation(10,10,False)
            node.move_speed = speed
            while not node.is_falling():
                node = node.generate_jump_angle_node(mmc)
            self.assertEqual(node.y, 7, "test for bump y " + str(speed))
            self.assertEqual(node.x, 14, "test for bump x " + str(speed))

        
    def test_multiple_jumps_from_same_column(self):
        #(not allowed)
        mmc = MochMapController()
        mmc.set_enterable_list([(10,9), (10,8), (10,7), (10,6), (10,5), (10,4)] )
        node = STEvaluator.STANode(None)
        node.setLocation(10,10, False)
        node.jump_start = 10
        node = node.generate_jump_node(mmc)
        self.assertIsNone(node)
 
class TestMapSliceController(unittest.TestCase):
    def test_checking_enter_tiles(self):
        # remember that we use c,r for maps, 
        # though for identity it doesn't matter
        slc = np.array([[1,0,0],[0,1,0],[0,0,1]])
        mc = STEvaluator.STMapSliceController(slc)
        self.assertEqual(mc.can_enter(0,0), False )
        self.assertEqual(mc.can_enter(0,1), True )
        self.assertEqual(mc.can_enter(0,2), True )
        self.assertEqual(mc.can_enter(1,0), True)
        self.assertEqual(mc.can_enter(1,1), False )
        self.assertEqual(mc.can_enter(1,2), True )
        self.assertEqual(mc.can_enter(2,0), True )
        self.assertEqual(mc.can_enter(2,1), True )
        self.assertEqual(mc.can_enter(2,2), False )
        self.assertEqual(mc.can_enter(-1,2), False )
        self.assertEqual(mc.can_enter(23,2), False )
        self.assertEqual(mc.can_enter(2,-2), True )
        self.assertEqual(mc.can_enter(2,22), True )
        
    def test_checking_if_alive(self):
        slc = np.array([[1,0,0],[0,1,0],[0,0,1]])
        mc = STEvaluator.STMapSliceController(slc)
        self.assertEqual(mc.is_alive(0,2), True )
        self.assertEqual(mc.is_alive(1,2), True )
        self.assertEqual(mc.is_alive(1,3), False )
        self.assertEqual(mc.is_alive(2,2), False )
        self.assertEqual(mc.is_alive(3,2), False )
        self.assertEqual(mc.is_alive(-1,2), False )
        self.assertEqual(mc.is_alive(1,-1), True )
        
    def test_if_won(self):
        slc = np.array([[1,0,0],[0,1,0],[0,0,1]])
        mc = STEvaluator.STMapSliceController(slc)
        self.assertEqual(mc.has_won(0,2), False )
        self.assertEqual(mc.has_won(1,2), False )
        self.assertEqual(mc.has_won(1,1), False )
        self.assertEqual(mc.has_won(2,2), False ) # entering solid
        self.assertEqual(mc.has_won(2,1), True )
            
    def test_printing_map_slices(self):
        slc = np.array(COMPLEX_PATH)
        mc = STEvaluator.STMapSliceController(slc)
        col = 0
        for s in COMPLEX_PATH_MAP_STRINGS:
            ts = mc.get_map_column_as_string(col)
            col += 1
            #print(ts)
            self.assertEqual(ts,s)
       
class TestPriorityQueue(unittest.TestCase):
    def test_adding_to_queue_reverse_order(self):
        first = STEvaluator.STANode(None)
        first.priority = 1
        second = STEvaluator.STANode( None)
        second.priority = 2
        third = STEvaluator.STANode( None)
        third.priority = 3
        pq = STEvaluator.STPriorityQueue()
        pq.enqueue(third)
        pq.enqueue(second)
        pq.enqueue(first)
        self.assertEqual(pq.dequeue().priority, 1)
        self.assertEqual(pq.dequeue().priority, 2)
        self.assertEqual(pq.dequeue().priority, 3)
        self.assertIsNone(pq.dequeue())
    
    def test_adding_to_queue_in_order(self):
        first = STEvaluator.STANode(None)
        first.priority = 1
        second = STEvaluator.STANode( None)
        second.priority = 2
        third = STEvaluator.STANode( None)
        third.priority = 3
        pq = STEvaluator.STPriorityQueue()
        pq.enqueue(first)
        pq.enqueue(second)
        pq.enqueue(third)
        self.assertEqual(pq.dequeue().priority, 1)
        self.assertEqual(pq.dequeue().priority, 2)
        self.assertEqual(pq.dequeue().priority, 3)
        self.assertIsNone(pq.dequeue())

    def test_adding_to_queue_in_mixed_order(self):
        first = STEvaluator.STANode(None)
        first.priority = 1
        second = STEvaluator.STANode(None)
        second.priority = 2
        second_b = STEvaluator.STANode(None)
        second_b.priority = 2
        third = STEvaluator.STANode( None)
        third.priority = 3
        third_b = STEvaluator.STANode(None)
        third_b.priority = 3
        third_c = STEvaluator.STANode(None)
        third_c.priority = 3
        fourth = STEvaluator.STANode(None)
        fourth.priority = 4
        pq = STEvaluator.STPriorityQueue()
        pq.enqueue(first)
        pq.enqueue(third)
        pq.enqueue(second)
        pq.enqueue(third_b)
        pq.enqueue(second_b)
        pq.enqueue(fourth)
        pq.enqueue(third_c)

        self.assertEqual(pq.dequeue().priority, 1)
        self.assertEqual(pq.dequeue().priority, 2)
        self.assertEqual(pq.dequeue().priority, 2)
        self.assertEqual(pq.dequeue().priority, 3)
        self.assertEqual(pq.dequeue().priority, 3)
        self.assertEqual(pq.dequeue().priority, 3)
        self.assertEqual(pq.dequeue().priority, 4)
        self.assertIsNone(pq.dequeue())


class TestSTAStarPath(unittest.TestCase):
    def test_walk_path(self):
        slc = np.array(MAP_WALKING)
        mc = STEvaluator.STMapSliceController(slc)
        astar = STEvaluator.STAStarPath(mc, 0,5)
        path = astar.find_path()
        self.assertIsNotNone(path)

    def test_blocked_path(self):
        slc = np.array([[1,0,0,0,0,0,1],[1,0,0,0,0,0,1],[1,0,0,0,0,0,1],
               [1,0,0,0,0,0,1],[1,1,1,1,1,1,1],[0,0,0,0,0,0,1],
               [0,0,0,0,0,0,1] ])
        mc = STEvaluator.STMapSliceController(slc)
        astar = STEvaluator.STAStarPath(mc, 0,5)
        path = astar.find_path()
        self.assertEqual(path, [])
        node = astar.find_furthest_path_node()
        self.assertEqual(node.x, 3)

    def test_complex_path(self):
        slc = np.array([ [0,0,0,0,0,0,1],[0,0,0,0,0,0,1],[0,0,0,0,0,0,1],
                [0,0,0,0,0,0,1],[1,0,0,0,0,0,1],[1,0,0,1,0,0,0],
                [1,0,0,1,0,0,0],[1,0,0,1,0,0,0],[1,0,0,1,0,0,0],
                [1,0,0,0,0,0,0],[1,0,0,0,0,0,0],[1,0,0,0,0,0,0],
                [1,0,0,0,0,0,0],[1,0,0,0,0,0,0],[0,0,0,0,0,0,1],
                [0,0,0,0,0,0,1],[0,0,0,0,0,0,1], [0,0,0,0,0,0,1] ])
        mc = STEvaluator.STMapSliceController(slc)
        astar = STEvaluator.STAStarPath(mc, 0,5)
        node = astar.find_furthest_path_node()
        self.assertEqual(node.x, 17)

    def test_generating_path_map(self):
        pathxy = [(1,5), (2,4),(2,3),(2,2), (2,1),(2,0), (3,3), (4,3),(5,3)]
        path = []
        for point in pathxy:
            node = STEvaluator.STANode()
            node.x = point[0]
            node.y = point[1]
            path.append(node)
        mc = STEvaluator.STMapSliceController()
        astar = STEvaluator.STAStarPath(mc, 0,5)
        slc = astar.build_path_slice(6,6,path)
        #print(slc)
        for point in pathxy:
            self.assertEqual(slc[point[0], point[1]], 1)
        
    def test_get_path_encoding_set(self):
        slc = np.array([ [0,0,0,0,0,0,1],[0,0,0,0,0,0,1],[0,0,0,0,0,0,1],
                [0,0,0,0,0,0,1],[1,0,0,0,0,0,1],[1,0,0,1,0,0,0],
                [1,0,0,1,0,0,0],[1,0,0,1,0,0,0],[1,0,0,1,0,0,0],
                [1,0,0,0,0,0,0],[1,0,0,0,0,0,0],[1,0,0,0,0,0,0],
                [1,0,0,0,0,0,0],[1,0,0,0,0,0,0],[0,0,0,0,0,0,1],
                [0,0,0,0,0,0,1],[0,0,0,0,0,0,1], [0,0,0,0,0,0,1] ])
        mc = STEvaluator.STMapSliceController(slc)
        astar = STEvaluator.STAStarPath(mc, 0,5)
        test_set = astar.get_path_encoding_set(7, 5,True)
        #print(test_set)
        self.assertEqual(test_set.shape[0],14)
        self.assertEqual(test_set.shape[1],35)
        test_set = astar.get_path_encoding_set(8, 5,True, 1)
        print(test_set)
        self.assertEqual(test_set.shape[0],14)
        self.assertEqual(test_set.shape[1],40)
           
            
    
if __name__ == '__main__':
    unittest.main()
