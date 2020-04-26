import numpy as np
import random
import stparser

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

if __name__ == '__main__':
    mm = stparser.MapManager()
    gnm = GenerateNoisyMap(mm)
    gnm.load_frequency_table("solid_tile_frequency.csv")
    slice = gnm.generate_random_slice()
    print(slice)
