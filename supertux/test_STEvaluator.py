# -*- coding: utf-8 -*-
"""
Created on Fri Dec 27 15:27:15 2019

@author: Billy D. Spelchan
"""

import unittest

class MochMapController:
    def __init__(self):
        self.enter_list = []
    
    def set_enterable_list(self, lst):
        self.enter_list = lst
        
    def canEnter(self, row, col):
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
        self.assertEqual(mmc.canEnter(1,2), True)
        self.assertEqual(mmc.canEnter(2,1), True)
        self.assertEqual(mmc.canEnter(2,2), False)

    
if __name__ == '__main__':
    unittest.main()
