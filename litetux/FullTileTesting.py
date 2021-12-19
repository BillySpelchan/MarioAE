import random

import numpy as np
import tensorflow as tf
from litetux import LTModel, LTMap
import math
import time

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
    def __init__(self, slice_cols, slice_rows, hidden=.5, encoded=.25,optimizer='adam', loss='mean_squared_error'):
        """
        :param slice_cols:
        :param slice_rows:
        :param hidden: % size of hidden layer (.5 = 50%) or absolute size if > 1
        :param encoded: % size of hidden layer (.5 = 50%) or absolute size if > 1
        """
        self.tile_bits = 16
        self.rows = slice_rows
        self.cols = slice_cols
        self.model = LTModel.LTModel()
        self.in_nodes = slice_cols * slice_rows * self.tile_bits
        if hidden > 1:
            h_nodes = hidden
        else:
            h_nodes = math.floor(self.in_nodes * hidden)
        if encoded > 1:
            e_nodes = encoded
        else:
            e_nodes = math.floor(self.in_nodes * encoded)
        self.model.create_model(self.in_nodes, h_nodes, e_nodes, optimizer=optimizer, loss=loss)

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

    def build_slice_set(self, file_list, chunks=False):
        slice_set = None
        ltm = LTMap.LiteTuxMap(1, 1)
        step_size = self.cols if chunks else 1
        for filename in file_list:
            print("processing ", filename)
            ltm.load(filename)
            end_col = ltm.width - self.cols
            for c in range(0, end_col, step_size):
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

    def save(self, filename = "ohemodel.h5"):
        self.model.save(filename);


class BitplainEncoder(OneHotEncoder):
    def __init__(self, slice_cols, slice_rows, hidden=.5, encoded=.25, optimizer='adam', loss='mean_squared_error'):
        super().__init__(slice_cols, slice_rows, hidden, encoded)
        self.tile_bitplains=4
        self.rows = slice_rows
        self.cols = slice_cols
        self.model = LTModel.LTModel()
        self.in_nodes = slice_cols * slice_rows * self.tile_bitplains
        if hidden > 1:
            h_nodes = hidden
        else:
            h_nodes = math.floor(self.in_nodes * hidden)
        if encoded > 1:
            e_nodes = encoded
        else:
            e_nodes = math.floor(self.in_nodes * encoded)
        self.model.create_model(self.in_nodes, h_nodes, e_nodes, optimizer=optimizer, loss=loss)
        pass

    def encode_slice(self, lt_map, start_col):
        slc = np.zeros((self.in_nodes))
        for c in range(self.cols):
            for r in range(self.rows):
                t = lt_map.get_tile(c + start_col, r)
                for b in range(self.tile_bitplains):
                    mask = 1 << b
                    bit = 1 if (t & mask) > 0 else 0
                    slc[c*self.rows*self.tile_bitplains+r*self.tile_bitplains+b] = bit
        return slc

    def decode_slice(self, slc, target_map, start_col):
        slc_offset = 0
        for c in range(self.cols):
            for r in range(self.rows):
                t = 0
                for b in range(self.tile_bitplains):
                    mask = 1 << b
                    try:
                        if slc[slc_offset] > 0.4:
                            t += mask
                    except:
                        print("scl for " ,slc_offset, " is ", slc[slc_offset])
                    slc_offset += 1
                target_map.set_tile(c+start_col, r, t)

    def save(self, filename="bpemodel.h5"):
        self.model.save(filename)

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


def test_model(train_set, test_set, model, filename=None, prefix="test", epochs=300):
    """:key
    """
    training = model.build_slice_set(train_set)
    print("debug - start training " + prefix)
    tmr = time.process_time_ns()
    model.train(training, training, epochs)
    train_time = time.process_time_ns() - tmr
    print("debug - start testing")
    true_map = LTMap.LiteTuxMap(1,1)
    for lvlfile in test_set:
        s = prefix + "," + str(train_time) + "," + lvlfile+"," + str(epochs) + ","
        lvl_chunks = model.build_slice_set([lvlfile], True)
        true_map.load(lvlfile)
        predicted_map = LTMap.LiteTuxMap(true_map.width, true_map.height)
        for i in range(lvl_chunks.shape[0]):
            slc = model.predict(lvl_chunks[i])
            model.decode_slice(slc[0],predicted_map,i*model.cols)
        print(predicted_map.to_vertical_string())
        test = MapTest(true_map, predicted_map)
        s+= str(test.get_total_tile_errors()) + ","
        s+= str(test.get_average_tile_hamming_error()) + ","
        s+= str(test.get_average_distance_error()) + ","

        print(s)
        if filename is not None:
            with open(filename, "a") as f:
                f.write(s)
                f.write("\n")


def batch_find_best(train, test):
    for h in range(4, 10, 1):
        for e in range(1, h, 1):
            for ep in range (100, 600, 100):
                print("model size ", h/10, e/10, ep)
                settings = str(h/10)+";"+str(e/10)
                ohe = OneHotEncoder(4, 14, h/10, e/10)
                test_model(TRAIN_LEVELS, TEST_LEVELS, ohe, "fullTile.csv", "OneHot"+settings, ep)
                bpe = BitplainEncoder(4, 14, h/10, e/10)
                test_model(TRAIN_LEVELS, TEST_LEVELS, bpe, "fullTile.csv", "BitPlain"+settings, ep)

def find_best_bpe_config():
    #opts = ["poisson", "mean_squared_error","mean_absolute_error", "mean_squared_logarithmic_error", "cosine_similarity",
    opts = [ "hinge", "squared_hinge", "categorical_hinge"]
    for op in opts:
        tf.keras.backend.clear_session()
        for i in range(10):
            bpe = BitplainEncoder(4, 14, optimizer="adam", loss=op)
            test_model(TRAIN_LEVELS, TEST_LEVELS, bpe, "bpe_loss.csv", op + str(i))

def batch_find_best_bpe(train, test):
    for h in range(112, 168, 1):
        for e in range(25, 75, 1):
            tf.keras.backend.clear_session()
            for r in range(4):
                print("model size ", h, e)
                settings = str(h)+"_"+str(e)
                bpe = BitplainEncoder(4, 14, h, e)
                test_model(TRAIN_LEVELS, TEST_LEVELS, bpe, "fullTileBPE.csv", "BitPlain_"+settings)


def find_best_ohe_optimizer(loss="mean_squared_error"):
    #opts = ["SGD", "RMSProp", "adam", "adadelta", "adagrad",
    opts = ["adamax", "nadam"]
    for op in opts:
        tf.keras.backend.clear_session()
        for i in range(10):
            ohe = OneHotEncoder(4, 14, optimizer=op, loss=loss)
            test_model(TRAIN_LEVELS, TEST_LEVELS, ohe, "ohe_opt.csv", op + str(i))


def find_best_ohe_loss(optimizer="adadelta"):
    opts = ["binary_crossentropy", "categorical_crossentropy","poisson", "mean_squared_error","mean_absolute_error", "mean_squared_logarithmic_error", "cosine_similarity",  "hinge", "squared_hinge", "categorical_hinge"]
    for op in opts:
        tf.keras.backend.clear_session()
        for i in range(10):
            ohe = OneHotEncoder(4, 14, optimizer=optimizer, loss=op)
            test_model(TRAIN_LEVELS, TEST_LEVELS, ohe, "ohe_loss.csv", op + str(i))


def generate_ohe_test_forest(count, optimizer="adamax", loss="cosine_similarity"):
    for m in range(count):
        tf.keras.backend.clear_session()
        el = random.randrange(56, 448)
        hl = random.randrange(el, 840)
        ohe = OneHotEncoder(4, 14, hl, el, optimizer, loss)
        test_model(TRAIN_LEVELS, TEST_LEVELS, ohe, "ohe_test_forest.csv", "ohe_"+str(hl)+"_"+str(el))
        print("finished trial ", m)

def analyse_best_config_report(filename):
    results = {}
    with open(filename, 'r') as csv:
        for line in csv:
            data = line.split(',')
            # gen, time, lvl,epoch,erors,pct_hamming,pct_tile
            if len(data) > 3:
                optimizer = data[0][:-1]
                time = float(data[1])
                level = data[2]
                errors = int(data[4])
                # find records for optimizer and update time/count
                if optimizer in results:
                    r = results[optimizer]
                else:
                    r = {"count":0, "time":0.0 }
                    results[optimizer] = r
                r["count"] += 1
                r["time"] += time

                # update stats for level results
                if level in r:
                    stats = r[level]
                else:
                    stats = {"count":0, "errors":0, "best":9999999, "worst":0}
                    r[level] = stats
                stats["count"] += 1
                stats["errors"] += errors
                if errors < stats["best"]:
                    stats["best"] = errors
                if errors > stats["worst"]:
                    stats["worst"] = errors
    for k in results:
        r = results[k]
        print(k,r["time"]/r["count"],end=',')
        for name in TEST_LEVELS:
            stats = r[name]
            s = str(stats["best"])+','+str(stats["worst"])+','+str(stats["errors"]/stats["count"])+','
            print(s,end=' ')
        print()


def analyse_test_forest_encoder(source_csv_filename, report_csv_filename,
                                start_range=0, end_range=1000, bucket_size=1):
    num_buckets = int((end_range - start_range + 1) / bucket_size)
    print("allocating ", num_buckets, " buckets")
    buckets = []
    for i in range(num_buckets):
        buckets.append([{"best": 999999, "worst": 0, "sum": 0, "count": 0},
                        {"best": 999999, "worst": 0, "sum": 0, "count": 0},
                        {"best": 999999, "worst": 0, "sum": 0, "count": 0}])
    print("buckets allocated")
    with open(source_csv_filename, 'r') as file:
        for line in file:
            data = line.split(',')
            # gen, time, lvl,epoch,erors,pct_hamming,pct_tile
            shape = data[0].split('_')
            encoder = int(shape[2])
            encoder_bucket = (encoder - start_range) // bucket_size
            try:
                test_id = TEST_LEVELS.index(data[2])
            except:
                test_id = -1
            if encoder_bucket >= 0 and encoder_bucket < num_buckets and test_id >= 0:
                errors = int(data[4])
                stats = buckets[encoder_bucket][test_id]
                stats["count"] += 1
                stats["sum"] += errors
                if errors < stats["best"]:
                    stats["best"] = errors
                if errors > stats["worst"]:
                    stats["worst"] = errors

    s = "start_nodes, end_nodes, l1_best, l1_worst, l1_average, l2_best, l2_worst, l2_average, "
    s +="l3_best, l3_worst, l3_average\n"
    for bucket_id in range(num_buckets):
        s += str(bucket_id * bucket_size + start_range) + ','
        s += str((bucket_id+1) * bucket_size + start_range - 1) + ','
        for i in range(len(TEST_LEVELS)):
            stats = buckets[bucket_id][i]
            s += str(stats["best"]) + ',' + str(stats["worst"]) + ','
            if (stats["count"] > 0 ):
                s += str(stats["sum"] / stats["count"]) + ','
            else:
                s += "0,"
        s += "\n"
    print(s)
    with open(report_csv_filename, 'w') as file:
        file.write(s)


TRAIN_LEVELS = ["levels/mario-1-1.json",
                "levels/mario-2-1.json","levels/mario-3-1.json",
                "levels/mario-4-1.json","levels/mario-4-2.json", "levels/mario-5-1.json",
                "levels/mario-6-1.json","levels/mario-6-2.json",
                "levels/mario-7-1.json","levels/mario-8-1.json"]
TEST_LEVELS = ["levels/mario-1-2.json", "levels/mario-3-3.json", "levels/mario-6-1.json"]

if __name__ == "__main__":

    # ohe = OneHotEncoder(4, 14)
    # test_model(TRAIN_LEVELS, TEST_LEVELS, ohe)
    # bpe = BitplainEncoder(4, 14)
    # test_model(TRAIN_LEVELS, TEST_LEVELS, bpe, "fullTile.csv")
    #    batch_find_best(TRAIN_LEVELS, TEST_LEVELS)

    # find_best_bpe_config()
    # analyse_bpe_config_report("bpe_loss.csv")
    # batch_find_best_bpe(TRAIN_LEVELS, TEST_LEVELS)
    # find_best_ohe_optimizer()
    # analyse_best_config_report("ohe_opt.csv")
    # find_best_ohe_loss("adamax")
    # analyse_best_config_report("ohe_loss.csv")
    # analyse_test_forest_encoder("fullTileBPE.csv", "bpe_encoder_size_performance.csv",
    #                            25, 75, 1)
    # generate_ohe_test_forest(100)
    # print("calling analyse test forest encoder")
    # analyse_test_forest_encoder("ohe_test_forest.csv", "ohe_encoder_size_performance.csv",
    #                            56, 448, 10)
    print("creating bpe")
    bpe = BitplainEncoder(4, 14)
    print("training")
    test_model(TRAIN_LEVELS, TEST_LEVELS, bpe)
    print("saving bpe")
    bpe.model.save()
