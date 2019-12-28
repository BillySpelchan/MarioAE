# -*- coding: utf-8 -*-
"""
Created on Fri Dec 27 15:27:15 2019

@author: Billy D. Spelchan
"""

import unittest
import STEvaluator

class MochMapController:
    def __init__(self):
        self.enter_list = []
    
    def set_enterable_list(self, lst):
        self.enter_list = lst
        
    def can_enter(self, row, col):
        result = False
        for loc in self.enter_list:
            if (loc[0] == row) and (loc[1] == col):
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
