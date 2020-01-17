# -*- coding: utf-8 -*-
"""
Created on Sat Jan 11 13:08:38 2020

@author: spelc
"""
import unittest
import numpy as np
import stparser
import STEvaluator

import FindBestAutoencoder


class MochModel:
    def clean_prediction(self, slc, prediction = None):
        predict = np.copy(slc)
        for r in range(slc.shape[0]):
            if r%2==1:
                predict[r] = slc[r]
            else:
                predict[r] = 1 if slc[r] == 0 else 0
        return predict

class TestFindBestAutoencoder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mm = stparser.MapManager()
        cls.level = cls.mm.get_map("levels/test/burnnmelt.stl")
        cls.solid_map = cls.level.get_combined_solid()

    def test_compare_env_encoding(self):
        first = np.array([1,1,1,1,0,0,0,0])
        second = np.array([1,0,0,1,1,0,0,1])
        expected = np.array([1,3,3,1,2,0,0,2], dtype=np.int8)
        fba = FindBestAutoencoder.FindBestAutoencoder(self.mm)
        comp = fba.compare_env_encoding(first, second)
        self.assertEqual(np.array_equal(comp, expected), True)
#        controller = STEvaluator.STMapSliceController(self.solid_map)
#        s = controller.get_map_column_as_string(10)

    def test_compare_env_encoding_to_col_string(self):
        first = np.array([1,1,1,1,0,0,0,0])
        second = np.array([1,0,0,1,1,0,0,1])
        expected = "XHHX\nO--O\n"
        fba = FindBestAutoencoder.FindBestAutoencoder(self.mm)
        comp = fba.compare_env_encoding_to_col_string(first, second,4)
        self.assertEqual(comp == expected, True)

    def test_compare_counts(self):
        expected = np.array([1,3,3,1,2,0,2,2], dtype=np.int8)
        fba = FindBestAutoencoder.FindBestAutoencoder(self.mm)
        self.assertEqual(fba.count_comparison_errors(expected), 5)
        self.assertEqual(fba.count_comparison_should_be_empty_errors(expected), 3)
        self.assertEqual(fba.count_comparison_should_be_solid_errors(expected), 2)
    
    """            
    def test_get_training_set(self):
        fba = FindBestAutoencoder.FindBestAutoencoder(self.mm)
        training_set = fba.get_training_set()
        print("training set 8 col shape is ", training_set.shape )
        self.assertGreater(training_set.shape[0], 1)
        self.assertEqual(training_set.shape[1], 36*8)
        training_set = fba.get_training_set(4)
        print("training set 4 col shape is ", training_set.shape )
        self.assertGreater(training_set.shape[0], 1)
        self.assertEqual(training_set.shape[1], 36*4)
        training_set = fba.get_training_set(36)
        print("training set 36 col shape is ", training_set.shape )
        self.assertGreater(training_set.shape[0], 1)
        self.assertEqual(training_set.shape[1], 36*36)

    def test_get_testing_set(self):
        fba = FindBestAutoencoder.FindBestAutoencoder(self.mm)
        testing_set = fba.get_testing_set()
        print("testing set 8 col shape is ", testing_set.shape )
        self.assertGreater(testing_set.shape[0], 1)
        self.assertEqual(testing_set.shape[1], 36*8)
        testing_set = fba.get_testing_set(4)
        print("testing set 4 col shape is ", testing_set.shape )
        self.assertGreater(testing_set.shape[0], 1)
        self.assertEqual(testing_set.shape[1], 36*4)
        testing_set = fba.get_testing_set(36)
        print("testing set 36 col shape is ", testing_set.shape )
        self.assertGreater(testing_set.shape[0], 1)
        self.assertEqual(testing_set.shape[1], 36*36)
    
    def test_build_and_train_model(self):
        fba = FindBestAutoencoder.FindBestAutoencoder(self.mm)
        model = fba.build_and_train_model(1, 16, 8, 100)
        self.assertIsNotNone(model)
        slc = np.array([1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1])
        predict = model.clean_prediction(slc)
        print(predict)
        comp = fba.compare_env_encoding(slc, predict)
        self.assertLess(fba.count_comparison_errors(comp), 36)
    """ 

    def test_test_model(self):
        fba = FindBestAutoencoder.FindBestAutoencoder(self.mm)
        model = MochModel()
        results = fba.test_model(model, 1)
        print("test model results: ", results) # (tiles, errors, skyerr, grderr) 
        self.assertGreater(results[0], 1)
        self.assertGreater(results[1], 1)
        self.assertEqual(results[2]+results[3], results[1])
        
        
    @classmethod
    def tearDownClass(cls):
        pass
    
if __name__ == '__main__':
    unittest.main()
