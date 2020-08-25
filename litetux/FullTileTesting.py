from litetux import LTModel, LTMap
import math


class OneHotEncoder:
    def __init__(self, slice_rows, slice_cols, hidden=.5, encoded=.25):
        self.rows = slice_rows
        self.cols = slice_cols
        self.model = LTModel.LTModel()
        in_nodes = slice_cols * slice_rows * 16
        h_nodes = math.floor(in_nodes * hidden)
        e_nodes = math.floor(in_nodes * encoded)
        self.model.create_model(in_nodes, h_nodes, e_nodes)

    def encoode_slice(self, lt_map, start_col):
        pass

    def decode_slice(self, slc, target_map, start_col):
        pass


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



def test_one_hot_encode():
    ohe = OneHotEncoder(4,4)
    lvl = LTMap.LiteTuxMap(4,4);
    pass

def test_one_hot_decode():
   pass


if __name__ == "__main__":
    test_map_test();
