# -*- coding: utf-8 -*-
"""
Created on Sat Jan 11 12:51:20 2020

@author: spelc
"""

import numpy as np
import STModel
import stparser
from keras import backend as K

class FindBestAutoencoder:
    def __init__(self, map_manager, rows_in_level = 36):
        self.rows_in_level = rows_in_level
        self.mm = map_manager

    """
        compares encodings returning a np byte matrix with 
            0 = both match with empty
            1 = both match with wall
            2 = should be empty but is wall
            3 = should be wall but is empty
    """
    def compare_env_encoding(self, original, derived):
        results = np.zeros(original.shape, dtype=np.int8)
        for indx in range(original.shape[0]):
            originalIsWall = original[indx] > .5
            derivedIsWall = derived[indx] > .5
            if originalIsWall:
                if derivedIsWall:
                    results[indx] = 1
                else:
                    results[indx] = 3
            else:
                if derivedIsWall:
                    results[indx] = 2
                else:
                    results[indx] = 0
        return results

    def compare_env_encoding_to_col_string(self, original, derived, rows):
        COMP_LETTERS = "-XOH"
                
        result = ""
        comp = self.compare_env_encoding(original, derived)
        indx = 0
        cols = original.shape[0] // rows
        for col in range(cols):
            #print(orig_strs[col], " | ", der_strs[col], ' | ', end='')
            for row in range(rows):
                result += COMP_LETTERS[comp[indx+rows-row-1]]
            indx += rows
            result += '\n'
        return result
    
    def count_comparison_errors(self, comp_result):
        results = 0
        for indx in range(comp_result.shape[0]):
            if comp_result[indx] > 1:
                results += 1
        return results
    
    def count_comparison_should_be_empty_errors(self, comp_result):
        results = 0
        for indx in range(comp_result.shape[0]):
            if comp_result[indx] == 2:
                results += 1
        return results

    def count_comparison_should_be_solid_errors(self, comp_result):
        results = 0
        for indx in range(comp_result.shape[0]):
            if comp_result[indx] == 3:
                results += 1
        return results
    

    def get_training_set(self, cols=8, overlap=True):
        training_set = self.mm.get_env_encoding_sets(\
                        [ "levels/bonus3/but_no_one_can_stop_it.stl",
                        "levels/bonus3/crystal sunset.stl",
                        "levels/bonus3/hanging roof.stl",
                        "levels/test/burnnmelt.stl ",
                        "levels/test/short_fuse.stl",
                        "levels/test/spike.stl",
                        "levels/test/tilemap_disco.stl",
                        "levels/test_old/auto.stl",
                        "levels/world1/frosted_fields.stl",
                        "levels/world1/somewhat_smaller_bath.stl",
                        "levels/world1/yeti_cutscene.stl"], 
                        self.rows_in_level, cols, overlap)
        return training_set

    def get_testing_set(self, cols=8, overlap=False):
        testing_set = self.mm.get_env_encoding_sets(\
                        [ "levels/bonus3/Global_Warming.stl",
                        "levels/incubator/fall_kugelblitz.stl",
                        "levels/test_old/water.stl",
                        "levels/world2/besides_bushes.stl",], 
                        self.rows_in_level, cols, overlap)
        return testing_set

    def build_and_train_model(self, cols, hidden, encode, epochs):
        model = STModel.STModel()
        model.create_model(cols*self.rows_in_level, hidden, encode)
        training_set = self.get_training_set(cols)
        model.train_model(training_set, epochs)
        return model
    
    def test_model(self, model, cols):
        total_tiles = 0
        total_errors = 0
        total_sky_errors = 0
        total_ground_errors = 0
        # actual testing    
        testing_set = self.get_testing_set(cols)
        for test in testing_set:
            predict = model.clean_prediction(test)
            comp = self.compare_env_encoding(test, predict)
            total_tiles += (cols * self.rows_in_level)
            total_errors += self.count_comparison_errors(comp)
            total_sky_errors += self.count_comparison_should_be_empty_errors(comp)
            total_ground_errors += self.count_comparison_should_be_solid_errors(comp)
        return (total_tiles, total_errors, total_sky_errors, total_ground_errors)

    def internal_write_csv_entry(self, filename, cols, hid, enc, eps, results):
        # build csv row
        entry = [cols,hid,enc,eps, results[0], results[1], results[2]]
        s = ''
        for item in entry:
            s += str(item) + ','
        s +=str(results[3])
        # write row to file
        f = open(filename, 'a')
        f.write(s)
        f.write('\n')
        f.close()
        # return csv row as string
        return s
        
    
    def perform_baseline_test(self, csv_filename = "temp.csv"):        
        for c in range(1,37):
            for e in range(3):
                model = self.build_and_train_model(c, c*18, c*9, e*50)
                results = fba.test_model(model, c)
                print(c,' @ ' , e, ' results ', results)
                self.internal_write_csv_entry(csv_filename, c, c*18, c*9, e*50, results)
                K.clear_session()
                del model

    def perform_batch_test(self, col, epoch, csv_filename = "temp.csv"):
        bits = col * self.rows_in_level
        step = bits//10 # 10% step
        for hidden in range(bits//5, bits-1,step):
            for encode in range(bits//20, hidden, step):
                model = self.build_and_train_model(col, hidden, encode, epoch)
                results = fba.test_model(model, col)
                s = self.internal_write_csv_entry(csv_filename, col, hidden, encode, epoch, results)
                print(s)
                K.clear_session()
                del model
                    
if __name__ == '__main__':
    mm = stparser.MapManager()
    fba = FindBestAutoencoder(mm)
    for indx in range(3,5):
        fba.perform_batch_test(indx,100)
        fba.perform_batch_test(indx,150)
        fba.perform_batch_test(indx,200)
    for indx in range(7,37):
        fba.perform_batch_test(indx,100)
        fba.perform_batch_test(indx,150)
        fba.perform_batch_test(indx,200)


               