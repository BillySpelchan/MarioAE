# -*- coding: utf-8 -*-
"""
Created on Sat Jan 11 12:51:20 2020

@author: spelc
"""

import numpy as np
import STModel
import stparser
import STEvaluator
from keras import backend as K
import matplotlib.pyplot as plt

class FindBestAutoencoder:
    def __init__(self, map_manager, rows_in_level = 36):
        self.rows_in_level = rows_in_level
        self.mm = map_manager

    TRAINING_SET = [ "levels/bonus3/but_no_one_can_stop_it.stl",                        
                        "levels/bonus3/crystal sunset.stl",
                        "levels/bonus3/hanging roof.stl",
                        "levels/test/burnnmelt.stl ",
                        "levels/test/short_fuse.stl",
                        "levels/test/spike.stl",
                        "levels/test/tilemap_disco.stl",
                        "levels/test_old/auto.stl",
                        "levels/world1/frosted_fields.stl",
                        "levels/world1/somewhat_smaller_bath.stl",
                        "levels/world1/yeti_cutscene.stl"]
    
    TESTING_SET = [ "levels/bonus3/Global_Warming.stl",
                        "levels/incubator/fall_kugelblitz.stl",
                        "levels/test_old/water.stl",
                        "levels/world2/besides_bushes.stl"]
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
                        self.TRAINING_SET, 
                        self.rows_in_level, cols, overlap)
        return training_set

    def get_testing_set(self, cols=8, overlap=False):
        testing_set = self.mm.get_env_encoding_sets(\
                        self.TESTING_SET, 
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
                results = self.test_model(model, c)
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
                results = self.test_model(model, col)
                s = self.internal_write_csv_entry(csv_filename, col, hidden, encode, epoch, results)
                print(s)
                K.clear_session()
                del model
  

     # --------------------


    def get_path_encoding_sets(self, map_names, rows, cols, overlap):
        enc_set = None
        for map_name in map_names:
            level = self.mm.get_map(map_name)
            solid_map = level.get_combined_solid()
            controller = STEvaluator.STMapSliceController(solid_map)
            start = level.get_starting_location()
            astar = STEvaluator.STAStarPath(controller, int(start[0]), int(start[1]))
            enc = astar.get_path_encoding_set(rows, cols, overlap, rows - controller.get_num_rows())
            if enc_set is not None:
                enc_set = np.append(enc_set, enc, axis=0)
            else:
                enc_set = enc
        return enc_set

    def get_path_training_set(self, cols=8, overlap=True):
        training_set = self.get_path_encoding_sets(\
                        self.TRAINING_SET, 
                        self.rows_in_level, cols, overlap)
        return training_set
    
    def get_path_testing_set(self, cols=8, overlap=False):
        testing_set = self.get_path_encoding_sets(\
                        self.TESTING_SET, 
                        self.rows_in_level, cols, overlap)
        return testing_set
   

    def build_and_train_path_model(self, cols, hidden, encode, epochs):
        model = STModel.STModel()
        model.create_model(cols*self.rows_in_level, hidden, encode)
        training_set = self.get_path_training_set(cols)
        model.train_model(training_set, epochs)
        return model
    
    def test_path_model(self, model, cols):
        total_tiles = 0
        total_errors = 0
        total_sky_errors = 0
        total_ground_errors = 0
        # actual testing    
        testing_set = self.get_path_testing_set(cols)
        for test in testing_set:
            predict = model.clean_prediction(test)
            comp = self.compare_env_encoding(test, predict)
            total_tiles += (cols * 35)
            total_errors += self.count_comparison_errors(comp)
            total_sky_errors += self.count_comparison_should_be_empty_errors(comp)
            total_ground_errors += self.count_comparison_should_be_solid_errors(comp)
        return (total_tiles, total_errors, total_sky_errors, total_ground_errors)


     # --------------------

    def get_mixed_training_set(self, cols=8, overlap=True):      
        env_training_set = self.mm.get_env_encoding_sets(\
                        self.TRAINING_SET, 
                        self.rows_in_level, cols, overlap)
        path_training_set = self.get_path_encoding_sets(\
                        self.TRAINING_SET, 
                        self.rows_in_level, cols, overlap)
        training_set = np.zeros((env_training_set.shape[0], cols*2*self.rows_in_level))
        for indx in range(env_training_set.shape[0]):
            for tile in range(cols*self.rows_in_level):
                training_set[indx][tile] = env_training_set[indx][tile]
                training_set[indx][tile+cols*self.rows_in_level] = path_training_set[indx][tile]
            
        return training_set

    
    def get_mixed_testing_set(self, cols=8, overlap=False):
        env_testing_set = self.mm.get_env_encoding_sets(\
                        self.TESTING_SET, 
                        self.rows_in_level, cols, overlap)
        path_testing_set = self.get_path_encoding_sets(\
                        self.TESTING_SET, 
                        self.rows_in_level, cols, overlap)
        testing_set = np.zeros((env_testing_set.shape[0], cols*2*self.rows_in_level))
        for indx in range(env_testing_set.shape[0]):
            for tile in range(cols*self.rows_in_level):
                testing_set[indx][tile] = env_testing_set[indx][tile]
                testing_set[indx][tile+cols*self.rows_in_level] = path_testing_set[indx][tile]
            
        return testing_set

    def build_and_train_mixed_model(self, cols, hidden, encode, epochs):
        model = STModel.STModel()
        model.create_model(cols*self.rows_in_level*2, hidden, encode)
        training_set = self.get_mixed_training_set(cols)
        model.train_model(training_set, epochs)
        return model
    
    def test_mixed_model(self, model, cols):
        total_tiles = 0
        total_errors = 0
        total_sky_errors = 0
        total_ground_errors = 0
        # actual testing    
        testing_set = self.get_mixed_testing_set(cols)
        for test in testing_set:
            predict = model.clean_prediction(test)
            comp = self.compare_env_encoding(test, predict)
            total_tiles += (cols * self.rows_in_level * 2)
            total_errors += self.count_comparison_errors(comp)
            total_sky_errors += self.count_comparison_should_be_empty_errors(comp)
            total_ground_errors += self.count_comparison_should_be_solid_errors(comp)
        return (total_tiles, total_errors, total_sky_errors, total_ground_errors)

    def test_mixed_model_environment(self, model, cols):
        total_tiles = 0
        total_errors = 0
        total_sky_errors = 0
        total_ground_errors = 0
        # actual testing    
        testing_set = self.get_mixed_testing_set(cols)
        for test in testing_set:
            predict = model.clean_prediction(test)
            comp = self.compare_env_encoding(test[0:cols*self.rows_in_level], predict[0:cols*self.rows_in_level])
            total_tiles += (cols * self.rows_in_level)
            total_errors += self.count_comparison_errors(comp)
            total_sky_errors += self.count_comparison_should_be_empty_errors(comp)
            total_ground_errors += self.count_comparison_should_be_solid_errors(comp)
        return (total_tiles, total_errors, total_sky_errors, total_ground_errors)
        

    def perform_baseline_mixed_test(self, csv_filename = "mixed.csv"):        
        for c in range(1,37):
            for e in range(3):
                model = self.build_and_train_mixed_model(c, c*36, c*18, e*100+100)
                results = self.test_mixed_model_environment(model, c)
                print(c,' @ ' , e, ' results ', results)
                self.internal_write_csv_entry(csv_filename, c, c*36, c*18, e*100*+100, results)
                K.clear_session()
                del model

    def perform_batch_mixed_test(self, col, epoch, csv_filename = "mixed.csv"):
        bits = col * self.rows_in_level * 2
        step = bits//10 # 10% step
        for hidden in range(bits//5, bits-1,step):
            for encode in range(bits//20, hidden, step):
                model = self.build_and_train_mixed_model(col, hidden, encode, epoch)
                results = self.test_mixed_model_environment(model, col)
                s = self.internal_write_csv_entry(csv_filename, col, hidden, encode, epoch, results)
                print(s)
                K.clear_session()
                del model
                
    # -----------------------

    def build_and_train_path_to_env_model(self, cols, hidden, encode, epochs):
        model = STModel.STModel()
        model.create_model(cols*self.rows_in_level, hidden, encode)
        out_set = self.mm.get_env_encoding_sets(\
                        self.TRAINING_SET, 
                        self.rows_in_level, cols, True)
        in_set = self.get_path_encoding_sets(\
                        self.TRAINING_SET, 
                        self.rows_in_level, cols, True)
        
        model.train_for_different_output(in_set, out_set, epochs)
        return model

    def test_path_to_env_model(self, model, cols):
        total_tiles = 0
        total_errors = 0
        total_sky_errors = 0
        total_ground_errors = 0
        # actual testing    
        out_set = self.mm.get_env_encoding_sets(\
                        self.TESTING_SET, 
                        self.rows_in_level, cols, True)
        in_set = self.get_path_encoding_sets(\
                        self.TESTING_SET, 
                        self.rows_in_level, cols, True)
        for indx in range (len(out_set)):
            test = in_set[indx]
            predict = model.clean_prediction(test)
            comp = self.compare_env_encoding(out_set[indx], predict)
            total_tiles += (cols * self.rows_in_level)
            total_errors += self.count_comparison_errors(comp)
            total_sky_errors += self.count_comparison_should_be_empty_errors(comp)
            total_ground_errors += self.count_comparison_should_be_solid_errors(comp)
        return (total_tiles, total_errors, total_sky_errors, total_ground_errors)
     
    def perform_baseline_path_to_env_test(self, csv_filename = "p2e.csv"):
        for c in range(1,37):
            for e in range(3):
                model = self.build_and_train_path_to_env_model(c, c*36, c*18, e*100+150)
                results = self.test_path_to_env_model(model, c)
                print(c,' @ ' , e, ' results ', results)
                self.internal_write_csv_entry(csv_filename, c, c*36, c*18, e*100+150, results)
                K.clear_session()
                del model

    def perform_batch_path_to_env_test(self, col, epoch, csv_filename = "p2e.csv"):
        bits = col * self.rows_in_level
        step = bits//10 # 10% step
        for hidden in range(bits//5, bits-1,step):
            for encode in range(bits//20, hidden, step):
                model = self.build_and_train_path_to_env_model(col, hidden, encode, epoch)
                results = self.test_path_to_env_model(model, col)
                s = self.internal_write_csv_entry(csv_filename, col, hidden, encode, epoch, results)
                print(s)
                K.clear_session()
                del model
    
  
def test_autoencoding_paths():
    mm = stparser.MapManager()
    fba = FindBestAutoencoder(mm)
    #fba.perform_batch_test(7,200)
    print("Building model")
    model = fba.build_and_train_path_model(7, 140, 70, 200)
    print(fba.test_path_model(model, 7))    
    
def test_mixed_autoencoder():
    mm = stparser.MapManager()
    fba = FindBestAutoencoder(mm)
    print("Building model")
    model = fba.build_and_train_mixed_model(7, 140, 70, 200)
    print("mixed model results: ", fba.test_mixed_model(model, 7))    
    print("mixed model environment only results: ", fba.test_mixed_model_environment(model, 7))    

def test_path_to_env_autoencoder():
    mm = stparser.MapManager()
    fba = FindBestAutoencoder(mm)
    print("Building model")
    model = fba.build_and_train_path_to_env_model(7, 140, 70, 400)
    print(fba.test_path_to_env_model(model, 7))


class PlotTestResults:
    def __init__(self):
        pass

    def load_results_csv(self, csv_file_name):
        cols = []
        for _ in range(37):
            cols.append([])
        with open(csv_file_name, 'r') as csv:
            for line in csv:
                data = line.split(',')
                #col,size,hidden,epoch,tiles,error,gnd_err,sky_err

                try:
                    col = int(data[0].strip())
                    tiles = float(data[4].strip())
                    bad = float(data[5].strip())
                except ValueError:
                    print("Invalid line in csv: ", data)
                    continue
                if col < 0 or col > 36:
                    col = 0
                    print("Invalid column in csv: ", data)
                if tiles < 1:
                    print("Invalid tile count in csv: ", data)
                    continue
                cols[col].append(bad / tiles)
        return cols


    def generate_box_plot(self, plot_title, csv_file_name, col_start=1, col_end=36, out_file=None):
        csv_data = self.load_results_csv(csv_file_name)
        plot_data = []
        for cntr in range(col_start, col_end+1):
            plot_data.append(csv_data[cntr])
        plt.clf()
        plt.boxplot(plot_data)
        plt.title(plot_title)
        plt.xlabel("Columns")
        plt.ylabel("Error rate")

        if out_file is not None:
            plt.savefig(out_file, dpi=600)
        else:
            plt.show()


    def plottest(self):
        xvals = np.arange(0, 10, .1)
        plt.plot(xvals, np.sin(xvals))
        plt.show()


if __name__ == '__main__':
    # test_autoencoding_paths()
    """
#    mm = stparser.MapManager()
#    fba = FindBestAutoencoder(mm)
#    fba.perform_baseline_path_to_env_test()
     
#    map_gen_model = fba.build_and_train_model(5, 117, 72, 150)
#    map_gen_model.save("mapgen5_117_72.h5")
#    for cols in range(6,7):#11):#do other ranges when idle
#        fba.perform_batch_path_to_env_test(cols, 150)
#        fba.perform_batch_path_to_env_test(cols, 250)
#        fba.perform_batch_path_to_env_test(cols, 350)
    """

    ptr = PlotTestResults()
    # ptr.plottest()
    ptr.generate_box_plot("Path Autoencoder Column Error Rate", "mixed.csv", 1,36, "pathAutoencoderBoxplot.png")

