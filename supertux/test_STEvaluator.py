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


class MochMapController:
    def __init__(self):
        self.enter_list = []
    
    def set_enterable_list(self, lst):
        self.enter_list = lst
        
    def can_enter(self, x, y):
        result = False
        for loc in self.enter_list:
            if (loc[0] == x) and (loc[1] == y):
                result = True
                break
        return result

    
class TestMochMapController(unittest.TestCase):
    def test_moch_map_controller(self):
        mmc = MochMapController()
        mmc.set_enterable_list([(1,2), (2,1)])
        self.assertEqual(mmc.can_enter(1,2), True)
        self.assertEqual(mmc.can_enter(2,1), True)
        self.assertEqual(mmc.can_enter(2,2), False)


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
        
            
        
       
class TestPriorityQueue(unittest.TestCase):
    def test_adding_to_queue_reverse_order(self):
        first = STEvaluator.STANode(None, 1)
        second = STEvaluator.STANode( None, 2)
        third = STEvaluator.STANode( None, 3)
        pq = STEvaluator.STPriorityQueue()
        pq.enqueue(third)
        pq.enqueue(second)
        pq.enqueue(first)
        self.assertEqual(pq.dequeue().time_taken, 1)
        self.assertEqual(pq.dequeue().time_taken, 2)
        self.assertEqual(pq.dequeue().time_taken, 3)
        self.assertIsNone(pq.dequeue())
    
    def test_adding_to_queue_in_order(self):
        first = STEvaluator.STANode(None, 1)
        second = STEvaluator.STANode(None, 2)
        third = STEvaluator.STANode(None, 3)
        pq = STEvaluator.STPriorityQueue()
        pq.enqueue(first)
        pq.enqueue(second)
        pq.enqueue(third)
        self.assertEqual(pq.dequeue().time_taken, 1)
        self.assertEqual(pq.dequeue().time_taken, 2)
        self.assertEqual(pq.dequeue().time_taken, 3)
        self.assertIsNone(pq.dequeue())

    def test_adding_to_queue_in_mixed_order(self):
        first = STEvaluator.STANode(None, 1)
        second = STEvaluator.STANode(None, 2)
        second_b = STEvaluator.STANode(None, 2)
        third = STEvaluator.STANode( None, 3)
        third_b = STEvaluator.STANode(None, 3)
        third_c = STEvaluator.STANode(None, 3)
        fourth = STEvaluator.STANode(None, 4)
        pq = STEvaluator.STPriorityQueue()
        pq.enqueue(first)
        pq.enqueue(third)
        pq.enqueue(second)
        pq.enqueue(third_b)
        pq.enqueue(second_b)
        pq.enqueue(fourth)
        pq.enqueue(third_c)

        self.assertEqual(pq.dequeue().time_taken, 1)
        self.assertEqual(pq.dequeue().time_taken, 2)
        self.assertEqual(pq.dequeue().time_taken, 2)
        self.assertEqual(pq.dequeue().time_taken, 3)
        self.assertEqual(pq.dequeue().time_taken, 3)
        self.assertEqual(pq.dequeue().time_taken, 3)
        self.assertEqual(pq.dequeue().time_taken, 4)
        self.assertIsNone(pq.dequeue())

   
if __name__ == '__main__':
    unittest.main()
