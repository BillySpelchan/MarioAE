# -*- coding: utf-8 -*-
"""
Created on Sat Jan 11 15:17:31 2020

@author: spelc
"""
import unittest

import numpy as np
import stparser
import STEvaluator

class TestMapManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mm = stparser.MapManager()
        cls.test_level_filename = "levels/test/burnnmelt.stl"
        cls.level = cls.mm.get_map(cls.test_level_filename)
        cls.solid_map = cls.level.get_combined_solid()

    def test_setup(self):
        controller = STEvaluator.STMapSliceController(self.solid_map)
        s = controller.get_map_column_as_string(10)
        #print (s)
        self.assertEqual(s, "X...........X............X.........")

    def test_slice_to_env_encoding(self):
        slc = np.array([[1,1,1,1,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,1]])
        expected = np.array([1,1,1,1,1,1,0,0,0,1,1,0,0,0,1,1,0,0,0,1,1,0,0,0,1,1,1,1,1,1], dtype=float)
        encoded = self.mm.slice_to_env_encoding(slc)
        self.assertEquals(np.array_equal(encoded, expected), True)

    def test_env_encoding_to_slice(self):
        expected = np.array([[1,1,1,1,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,1]])
        encoded = np.array([1,1,1,1,1,1,0,0,0,1,1,0,0,0,1,1,0,0,0,1,1,0,0,0,1,1,1,1,1,1], dtype=float)
        slc = self.mm.env_encoding_to_slice(encoded, 5)
        self.assertEquals(np.array_equal(slc, expected), True)

    def test_get_env_encoding_set(self):
        # slicing burnmelt map from column 3 
        test1 = np.array([0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1])
        training = self.mm.get_env_encoding_set(self.test_level_filename, 36, 1, True)
        self.assertEqual(training.shape, (100,36))
        self.assertEqual(np.array_equal(training[3], test1), True)
        test2 = np.array([0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,
                          0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,1])
        training = self.mm.get_env_encoding_set(self.test_level_filename, 36, 2, True)
        self.assertEqual(training.shape, (99,72))
        self.assertEqual(np.array_equal(training[3], test2), True)
        test3 = np.array([0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,
                          0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,1,
                          0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,1,1,0,1,0,0,0,0,0,0,0,0,0,0,0,1])
        training = self.mm.get_env_encoding_set(self.test_level_filename, 36, 3, True)
        self.assertEqual(training.shape, (98,108))
        self.assertEqual(np.array_equal(training[3], test3), True)
        test4 = np.array([0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,
                          0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,1,
                          0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,1,1,0,1,0,0,0,0,0,0,0,0,0,0,0,1,
                          0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1])
        training = self.mm.get_env_encoding_set(self.test_level_filename, 36, 4, True)
        self.assertEqual(training.shape, (97,144))
        self.assertEqual(np.array_equal(training[3], test4), True)
    
    @classmethod
    def tearDownClass(cls):
        pass
    
if __name__ == '__main__':
    unittest.main()
