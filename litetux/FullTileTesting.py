import numpy as np
from litetux import LTModel, LTMap
import math


class MapTest:
    def __init__(self, map_1, map_2, tile_bits=4):
        self.map_1 = map_1
        self.map_2 = map_2
        self.hamming = LTMap.LiteTuxMap(map_1.width, map_1.height)
        self.distances = LTMap.LiteTuxMap(map_1.width, map_1.height)
        self.total_tile_errors = 0
        self.total_hamming_error = 0
        self.total_distance_error = 0
        for c in range(self.map_1.width):
            for r in range(self.map_1.height):
                t1 = map_1.get_tile(c, r)
                t2 = map_2.get_tile(c, r)
                ham: int = 0
                mask = 1
                self.total_distance_error += abs(t1-t2)
                self.distances.set_tile(c, r, abs(t1-t2))
                for b in range(tile_bits):
                    if (t1 & mask) != (t2 & mask):
                        ham += 1
                    mask *= 2
                self.hamming.set_tile(c, r, ham)
                if ham > 0:
                    self.total_tile_errors += 1
                self.total_hamming_error += ham

    def get_total_tile_errors(self):
        return self.total_tile_errors

    def get_total_hamming_error(self):
        return self.total_hamming_error

    def get_average_tile_hamming_error(self):
        return self.total_hamming_error / (self.map_1.width * self.map_1.height)

    def hamming_errors_to_string(self):
        s = ""
        for c in range(self.hamming.width):
            for r in range(self.hamming.height):
                s = s + str(self.hamming.get_tile(c, r))
            s = s + "\n"
        return s

    def get_total_distance_error(self):
        return self.total_distance_error

    def get_average_distance_error(self):
        return self.total_distance_error / (self.map_1.width * self.map_1.height)

    def distance_errors_to_string(self):
        s = ""
        for c in range(self.distances.width):
            for r in range(self.distances.height):
                s = s + str(self.distances.get_tile(c, r))
                s = s + ' '
            s = s + "\n"
        return s

    def __str__(self):
        s = "total tile errors in map = " + str(self.get_total_tile_errors()) + "\n"
        s += "total hamming error = " + str(self.get_total_hamming_error()) + "\n"
        s += "average hamming error = " + str(self.get_average_tile_hamming_error()) + "\n"
        s += self.hamming_errors_to_string()
        s += "total distance errors = " + str(self.get_total_distance_error()) + "\n"
        s += "average distance error = " + str(self.get_average_distance_error()) + "\n"
        s += self.distance_errors_to_string()
        return s


# noinspection PyRedundantParentheses
class OneHotEncoder:
    def __init__(self, slice_cols, slice_rows, hidden=.5, encoded=.25):
        self.tile_bits = 16
        self.rows = slice_rows
        self.cols = slice_cols
        self.model = LTModel.LTModel()
        self.in_nodes = slice_cols * slice_rows * self.tile_bits
        h_nodes = math.floor(self.in_nodes * hidden)
        e_nodes = math.floor(self.in_nodes * encoded)
        self.model.create_model(self.in_nodes, h_nodes, e_nodes)

    def encode_slice(self, lt_map, start_col):
        slc = np.zeros((self.in_nodes))
        for c in range(self.cols):
            for r in range(self.rows):
                t = lt_map.get_tile(c+start_col, r)
                slc[c*self.rows*self.tile_bits+r*self.tile_bits+t] = 1
        return slc

    def decode_slice(self, slc, target_map, start_col):
        slc_offset = 0
        for c in range(self.cols):
            for r in range(self.rows):
                t_index = 0
                t_weight = slc[slc_offset]
                slc_offset += 1
                for b in range(1, self.tile_bits):
                    if (slc[slc_offset] > t_weight):
                        t_weight = slc[slc_offset]
                        t_index = b
                    slc_offset += 1
                target_map.set_tile(c+start_col, r, t_index)

    def build_slice_set(self, file_list):
        slice_set = None
        ltm = LTMap.LiteTuxMap(1, 1)
        for filename in file_list:
            print("processing ", filename)
            ltm.load(filename)
            end_col = ltm.width - self.cols
            for c in range(end_col):
                if slice_set is None:
                    slice_set = np.reshape(self.encode_slice(ltm, c), (1, self.in_nodes))
                else:
                    slice_set = np.vstack([slice_set, np.reshape(self.encode_slice(ltm, c), (1, self.in_nodes))])
        return slice_set

    def train(self, in_set, out_set=None, epoch=150):
        ts = out_set if out_set is not None else in_set
        self.model.train_for_different_output(in_set, ts, epoch)

    def predict(self, slc):
        return self.model.predict_slice(slc)

SMALL_TEST_MAP = "{\"width\":4, \"height\":4, \"_mapData\":[[0,1,2,3],[4,5,6,7],[8,9,10,11],[12,13,14,15]]}"


def test_one_hot_encode():
    ohe = OneHotEncoder(4, 4)
    lvl = LTMap.LiteTuxMap(4, 4)
    lvl.from_json_string(SMALL_TEST_MAP)
    slc = ohe.encode_slice(lvl, 0)
    i = 0

    for r in range(4):
        for c in range(4):
            print(c,",",r,end=': ')
            for b in range(16):
                print(slc[i], end=" ")
                i += 1
            print()


def test_one_hot_decode():
    ohe = OneHotEncoder(4, 4)
    lvl = LTMap.LiteTuxMap(4, 4)
    lvl.from_json_string(SMALL_TEST_MAP)
    rmap = LTMap.LiteTuxMap(4,4)
    slc = ohe.encode_slice(lvl, 0)
    ohe.decode_slice(slc,rmap,0)
    print(rmap.to_vertical_string())
    mt = MapTest(lvl, rmap)
    print(mt)


if __name__ == "__main__":
    TRAIN_LEVELS = ["levels/mario-1-1.json",
                  "levels/mario-2-1.json","levels/mario-3-1.json",
                  "levels/mario-4-1.json","levels/mario-4-2.json","levels/mario-5-1.json",
                  "levels/mario-6-1.json","levels/mario-6-2.json",
                  "levels/mario-7-1.json","levels/mario-8-1.json"]
    TEST_LEVELS = ["levels/mario-1-2.json", "levels/mario-3-3.json", "levels/mario-6-1.json"]

    ohe = OneHotEncoder(4, 14)
    ls = ohe.build_slice_set(TRAIN_LEVELS)
    print(ls)
    print(ls.shape)
    ohe.train(ls)
    pred = ohe.predict(ls[0])
    slcmap = LTMap.LiteTuxMap(4,14)
    ohe.decode_slice(pred[0], slcmap, 0)
    print(slcmap.to_vertical_string())