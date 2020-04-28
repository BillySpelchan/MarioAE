import math

import numpy as np
import random
import stparser
import STModel

LEVEL_LIST = [ "levels/bonus3/but_no_one_can_stop_it.stl",
                        "levels/bonus3/crystal sunset.stl",
                        "levels/bonus3/hanging roof.stl",
                        "levels/test/burnnmelt.stl ",
                        "levels/test/short_fuse.stl",
                        "levels/test/spike.stl",
                        "levels/test/tilemap_disco.stl",
                        "levels/test_old/auto.stl",
                        "levels/world1/frosted_fields.stl",
                        "levels/world1/somewhat_smaller_bath.stl",
                        "levels/world1/yeti_cutscene.stl",
                        "levels/bonus3/Global_Warming.stl",
                        "levels/incubator/fall_kugelblitz.stl",
                        "levels/test_old/water.stl",
                        "levels/world2/besides_bushes.stl"]

class GenerateNoisyMap:
    def __init__(self, map_manager, rows_in_level=36, cols_in_level=7):
        self.map_manager = map_manager
        self.rows_in_level = rows_in_level
        self.cols_in_level = cols_in_level
        self.frequency_table = np.zeros((cols_in_level * rows_in_level))
        
    def calculate_frequency_from_levels(self, list_of_levels):
        slices = self.map_manager.get_env_encoding_sets(list_of_levels, 
                                               self.rows_in_level, 
                                               self.cols_in_level, 
                                               True)
        solid_counts = np.zeros(self.frequency_table.shape)
        sample_count = 0
        for slice in slices:
            sample_count += 1
            for indx in range(self.cols_in_level * self.rows_in_level):
                if (slice[indx] > .5):
                    solid_counts[indx] += 1
        self.frequency_table = solid_counts / sample_count
        print(self.frequency_table)

    def save_frequency_table(self, filename):
        f = open(filename, 'w')
        last_index = self.cols_in_level * self.rows_in_level - 1
        for indx in range(last_index):
            f.write(str(self.frequency_table[indx]))
            f.write(',')
        f.write(str(self.frequency_table[last_index]))
        f.write('\n')
        f.close()

    def load_frequency_table(self, filename):
        f = open(filename, 'r')
        s = f.readline()
        f.close()
        data = s.split(',')
        table_size = self.rows_in_level * self.cols_in_level
        if len(data) != table_size:
            print("Error in table...doesn't match specified size!")
        else:
            for indx in range(table_size):
                self.frequency_table[indx] = float(data[indx])
            print(self.frequency_table)

    def generate_random_slice(self, error_factor = 0.0):
        slice = np.zeros(self.frequency_table.shape)
        for indx in range(slice.shape[0]):
            rnd = random.random()
            if rnd <= self.frequency_table[indx]:
                slice[indx] = 1
            rnd = random.random()
            if rnd < error_factor:
                if (slice[indx] == 1):
                    slice[indx] = 0
                else:
                    slice[indx] = 1
        return slice


class LevelGenerator:
    def __init__(self, mm, width=7, height=36):
        self.slice_width = width
        self.slice_height = height
        self.noise_map = GenerateNoisyMap(mm)
        self.noise_map.load_frequency_table("solid_tile_frequency.csv")
        self.map_manager = mm
        self.tilemap = stparser.STTilemap()
        self.map = stparser.STLevel()
        self.map.add_tilemap(self.tilemap)
        self.model = None

    def set_noise_map(self, noise_map):
        self.noise_map = noise_map

    def set_model(self, model):
        self.model = model

    def create_model(self, source_maps = None):
        if source_maps is None:
            source_maps = LEVEL_LIST
        self.model = STModel.STModel()
        self.model.create_model(36*7, 36*5, 36*3+18)
        training = mm.get_env_encoding_sets(source_maps, 36,7,True)
        self.model.train_model(training, 200)

    def get_model_prediction(self, source_slice):
        if self.model is None:
            return source_slice
        lslice = np.reshape(source_slice, (1, 36 * 7))
        lslice = self.model.predict_slice(lslice)
        for indx in range(36 * 7):
            lslice[0][indx] = 1 if lslice[0][indx] > .5 else 0
        lslice = np.reshape(lslice, (self.slice_width, self.slice_height))
        return lslice

    def generate_block_level(self, num_cols):
        self.tilemap.create_empty_level(num_cols, 36)
        chunks = math.floor(num_cols / self.slice_width)
        for c in range(chunks):
            lslice = self.get_model_prediction(self.noise_map.generate_random_slice())
            self.tilemap.write_slice(lslice.reshape((7, 36)), 7 * c)
        return self.map

    def generate_slide_level(self, num_cols, col_to_keep):
        pass



def build_save_and_test_frequency_table(filename):
    mm = stparser.MapManager()
    gnm = GenerateNoisyMap(mm)
    print("Please wait...generating frequency table from levels")
    gnm.calculate_frequency_from_levels(LEVEL_LIST)
    print("Saving frequency table to csv file")
    gnm.save_frequency_table("solid_tile_frequency.csv")
    print("validating csv file")
    gnm2 = GenerateNoisyMap(mm)
    gnm2.load_frequency_table("solid_tile_frequency.csv")

def build_and_show_noise_level(mm, noisemap):
    test_level = stparser.STTilemap()
    test_level.create_empty_level(200,36)
    test_map = stparser.STLevel()
    for c in range(28):
        lslice = noisemap.generate_random_slice()
        test_level.write_slice(lslice.reshape((7,36)), 7*c)
    test_map.add_tilemap(test_level)
    map_slice = test_map.get_slice(0,200)
    stparser.show_image_in_window(stparser.generate_image_from_slice(map_slice))

def show_map(map):
    shape = map.get_map_size()
    map_slice = map.get_slice(0, shape[0])
    stparser.show_image_in_window(stparser.generate_image_from_slice(map_slice))

if __name__ == '__main__':
    mm = stparser.MapManager()
    gnm = GenerateNoisyMap(mm)
    gnm.load_frequency_table("solid_tile_frequency.csv")

    # build_and_show_noise_level(mm, gnm)
    gen = LevelGenerator(mm)
    # gen.create_model()
    #gen.model.save("st_generator.h5")
    model = STModel.STModel()
    model.create_model(36*7, 36*5, 36*3+18)
    model.load("st_generator.h5")
    gen.set_model(model)
    map = gen.generate_block_level(500)
    show_map(map)
