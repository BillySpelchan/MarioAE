import time
import numpy as np
import tensorflow as tf
from litetux import LTMap, FullTileTesting


def get_input_output_sets_for_model(model, level_list):
    ltm = LTMap.LiteTuxMap(1, 1)
    step_size = model.cols
    in_set = None
    out_set = None
    for lvl in level_list:
        ltm.load(lvl)
        slice_set = None
        end_col = ltm.width - model.cols
        for c in range(0, end_col, step_size):
            if slice_set is None:
                slice_set = np.reshape(model.encode_slice(ltm, c), (1, model.in_nodes))
            else:
                slice_set = np.vstack([slice_set, np.reshape(model.encode_slice(ltm, c), (1, model.in_nodes))])
        if in_set is None:
            in_set = slice_set[0:-1,:]
            out_set = slice_set[1:,:]
        else:
            in_set = np.vstack([in_set, slice_set[0:-1,:]])
            out_set = np.vstack([out_set, slice_set[1:, :]])

    return (in_set, out_set)


def test_model(train_set, test_set, model, filename=None, prefix="test", epochs=300):
    """:key
    """
    results = {"train_time": 0, "errors": [], "tiles": []}
    train_input, train_output = get_input_output_sets_for_model(model, train_set)
    print("debug - start training " + prefix)
    tmr = time.process_time_ns()
    model.train(train_input, train_output, epochs)
    train_time = time.process_time_ns() - tmr
    results["train_time"] = train_time
    print("debug - start testing")
    true_map = LTMap.LiteTuxMap(1,1)
    for lvlfile in test_set:
        s = prefix + "," + str(train_time) + "," + lvlfile+"," + str(epochs) + ","
        lvl_chunks = model.build_slice_set([lvlfile], True)
        true_map.load(lvlfile)
        predicted_map = LTMap.LiteTuxMap(true_map.width, true_map.height)
        model.decode_slice(lvl_chunks[0], predicted_map, 0)
        for i in range(lvl_chunks.shape[0]-1):
            slc = model.predict(lvl_chunks[i])
            model.decode_slice(slc[0],predicted_map,(i+1)*model.cols)
        print(predicted_map.to_vertical_string())
        test = FullTileTesting.MapTest(true_map, predicted_map)
        s+= str(test.get_total_tile_errors()) + ","
        #s+= str(predicted_map.width*predicted_map.height) + ","
        s+= str(test.get_average_tile_hamming_error()) + ","
        s+= str(test.get_average_distance_error()) + ","
        s+= str(true_map.width*true_map.height)
        results["errors"].append(test.get_total_tile_errors())
        results["tiles"].append(true_map.width * true_map.height)
        print(s)
        if filename is not None:
            with open(filename, "a") as f:
                f.write(s)
                f.write("\n")
        return results

def find_best_bpe_predictor_optimizer(loss="mean_squared_error"):
    opts = ["SGD", "RMSProp", "adam", "adadelta", "adagrad", "adamax", "nadam"]
    for op in opts:
        tf.keras.backend.clear_session()
        for i in range(10):
            bpe = FullTileTesting.BitplainEncoder(4, 14, optimizer=op, loss=loss)
            test_model(FullTileTesting.TRAIN_LEVELS, FullTileTesting.TEST_LEVELS,
                       bpe, "predict_bpe_opt.csv", op + str(i))

def find_best_bpe_predictor_loss(optimizer="adadelta"):
    opts = ["poisson", "mean_squared_error","mean_absolute_error", "mean_squared_logarithmic_error", "cosine_similarity", "hinge", "squared_hinge", "categorical_hinge"]
    for op in opts:
        tf.keras.backend.clear_session()
        for i in range(10):
            bpe = FullTileTesting.BitplainEncoder(4, 14, optimizer=optimizer, loss=op)
            test_model(FullTileTesting.TRAIN_LEVELS, FullTileTesting.TEST_LEVELS, bpe, "bpe_predictor_loss.csv", op + str(i))

def find_best_ohe_predictor_optimizer(loss="mean_squared_error"):
    opts = ["SGD", "RMSProp", "adam", "adadelta", "adagrad", "adamax", "nadam"]
    for op in opts:
        tf.keras.backend.clear_session()
        for i in range(10):
            ohe = FullTileTesting.OneHotEncoder(4, 14, optimizer=op, loss=loss)
            test_model(FullTileTesting.TRAIN_LEVELS, FullTileTesting.TEST_LEVELS,
                       ohe, "predict_ohe_opt.csv", op + str(i))

def find_best_ohe_predictor_loss(optimizer="RMSProp"):
    opts = ["binary_crossentropy", "categorical_crossentropy", "poisson", "mean_squared_error","mean_absolute_error", "mean_squared_logarithmic_error", "cosine_similarity", "hinge", "squared_hinge", "categorical_hinge"]
    for op in opts:
        tf.keras.backend.clear_session()
        for i in range(10):
            ohe = FullTileTesting.OneHotEncoder(4, 14, optimizer=optimizer, loss=op)
            test_model(FullTileTesting.TRAIN_LEVELS, FullTileTesting.TEST_LEVELS, ohe, "ohe_predictor_loss.csv", op + str(i))

def write_predictor_test_results(hidden_pct, encoded_pct, ohe_batch, bpe_batch, verbose=True):
    num_trials = len(ohe_batch)
    num_tests = len(ohe_batch[0]["errors"])
    # set up best/worst/average test results and process while building raw file
    best_ohe = [999999] * num_tests
    best_bpe = [999999] * num_tests
    worst_ohe = [0] * num_tests
    worst_bpe = [0] * num_tests
    total_errors_ohe = [0] * num_tests
    total_errors_bpe = [0] * num_tests

    total_train_time_bpe = 0
    total_train_time_ohe = 0

    with open("oheVbpe_prediction_raw.csv", "a") as f:
        # write the raw file while calculating bwa results
        for i in range(num_trials):
            s = str(hidden_pct) + "," + str(encoded_pct) + ","
            s += str(ohe_batch[i]["train_time"]) + "," + str(bpe_batch[i]["train_time"]) + ","
            total_train_time_ohe += ohe_batch[i]["train_time"]
            total_train_time_bpe += bpe_batch[i]["train_time"]

            ohe_errors = ohe_batch[i]["errors"]
            bpe_errors = bpe_batch[i]["errors"]
            tiles = ohe_batch[i]["tiles"]
            for t in range(num_tests):
                s += str(ohe_errors[t]) + "," + str(bpe_errors[t]) + ","
                total_errors_ohe[t] += ohe_errors[t]
                total_errors_bpe[t] += bpe_errors[t]
                if ohe_errors[t] < best_ohe[t]:
                    best_ohe[t] = ohe_errors[t]
                if bpe_errors[t] < best_bpe[t]:
                    best_bpe[t] = bpe_errors[t]
                if ohe_errors[t] > worst_ohe[t]:
                    worst_ohe[t] = ohe_errors[t]
                if bpe_errors[t] > worst_bpe[t]:
                    worst_bpe[t] = bpe_errors[t]
                s += str(ohe_errors[t]/tiles[t]) + "," + str(bpe_errors[t]/tiles[t]) + ","
            s += "\n"
            f.write(s)
            if verbose:
                print(s)

    with open("oheVbpe_prediction.csv", "a") as f:
        s = str(hidden_pct) + "," + str(encoded_pct) + ","
        s += str(total_train_time_ohe / num_trials) + "," + str(total_train_time_bpe / num_trials) + ","
        tiles = ohe_batch[0]["tiles"]
        for t in range(num_tests):
            s += str(best_ohe[t] / tiles[t]) + "," + str(best_bpe[t] / tiles[t]) + ","
            s += str(worst_ohe[t] / tiles[t]) + "," + str(worst_bpe[t] / tiles[t]) + ","
            s += str(total_errors_ohe[t] / num_trials / tiles[t]) + ","
            s += str(total_errors_bpe[t] / num_trials / tiles[t]) + ","
        s += "\n"
        f.write(s)
        if verbose:
            print(s)

def perform_predictor_comparison_tests():
    with open("oheVbpe_prediction_raw.csv", 'w') as f:
        f.write("hidden,encoding,OHE Train,BPE TRain,OHE Err1C,BPE ErrlC,OHE Err1,BPE Errl,OHE Err2C,BPE Err2C,OHE Err2,BPE Err2,OHE Err3C,BPE Err3C,OHE Err3,BPE Err3\n")
    with open("oheVbpe_prediction.csv", 'w') as f:
        f.write("hidden,Encoding,Time OHE,Time BPE,")
        f.write("OHE Best 1,BPE Best 1,OHE Worst 1, BPE Worst 1, OHE Avg. 1, BPE Avg. 1,")
        f.write("OHE Best 2,BPE Best 2,OHE Worst 2, BPE Worst 2, OHE Avg. 2, BPE Avg. 2,")
        f.write("OHE Best 3,BPE Best 3,OHE Worst 3, BPE Worst 3, OHE Avg. 3, BPE Avg. 3\n")

    for e in range(1, 6):
        for h in range(e+1, 9):
            tf.keras.backend.clear_session()
            ohe_results = []
            bpe_results = []
            for t in range(10):
                print(f"Test for {h/10},{e/10} trial{t}")
                ohe = FullTileTesting.OneHotEncoder(4, 14, h / 10, e / 10, optimizer="adamax", loss="cosine_similarity")
                ohe_results.append(test_model(FullTileTesting.TRAIN_LEVELS, FullTileTesting.TEST_LEVELS,ohe))
                bpe = FullTileTesting.BitplainEncoder(4, 14, h / 10, e / 10, optimizer="adam", loss="mean_squared_error")
                bpe_results.append(test_model(FullTileTesting.TRAIN_LEVELS, FullTileTesting.TEST_LEVELS,bpe))
            write_predictor_test_results(h / 10, e / 10, ohe_results, bpe_results)

def batch_find_best_predictor(train, test):
    for h in range(4, 10, 1):
        for e in range(1, h, 1):
            for ep in range (100, 600, 100):
                print("model size ", h/10, e/10, ep)
                settings = str(h/10)+";"+str(e/10)
                ohe = FullTileTesting.OneHotEncoder(4, 14, h/10, e/10, "RMSProp")
                test_model(FullTileTesting.TRAIN_LEVELS, FullTileTesting.TEST_LEVELS, ohe, "fullTilePrediction.csv", "OneHot"+settings, ep)
                bpe = FullTileTesting.BitplainEncoder(4, 14, h/10, e/10, "adadelta", "mean_squared_logarithmic_error")
                test_model(FullTileTesting.TRAIN_LEVELS, FullTileTesting.TEST_LEVELS, bpe, "fullTilePrediction.csv", "BitPlain"+settings, ep)

if __name__ == "__main__":
    find_best_bpe_predictor_optimizer()
    FullTileTesting.analyse_best_config_report("predict_bpe_opt.csv") #Adadelta best
    #find_best_bpe_predictor_loss()
    #FullTileTesting.analyse_best_config_report("bpe_predictor_loss.csv")#mean_squared_log
    #find_best_ohe_predictor_optimizer()
    #FullTileTesting.analyse_best_config_report("predict_ohe_opt.csv") #RMSProp best
    #find_best_ohe_predictor_loss()
    #FullTileTesting.analyse_best_config_report("ohe_predictor_loss.csv")#mean_absolute_error
    #batch_find_best_predictor(FullTileTesting.TRAIN_LEVELS, FullTileTesting.TEST_LEVELS)
    #perform_predictor_comparison_tests()