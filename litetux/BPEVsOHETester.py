from litetux import LTMap, FullTileTesting
import tensorflow as tf
import time


def train_and_test(model):
    results = {"train_time": 0, "test_time": 0, "errors": [], "tiles": []}

    # train the model
    training = model.build_slice_set(FullTileTesting.TRAIN_LEVELS)
    tstart = time.process_time()
    model.train(training, training, 300)
    tend = time.process_time()
    results["train_time"] = tend-tstart

    # test the model
    true_map = LTMap.LiteTuxMap(1, 1)
    tstart = time.process_time()
    for lvlfile in FullTileTesting.TEST_LEVELS:
        level_chunks = model.build_slice_set([lvlfile], True)
        true_map.load(lvlfile)
        results["tiles"].append(true_map.width * true_map.height)
        predicted_map = LTMap.LiteTuxMap(true_map.width, true_map.height)
        for i in range(level_chunks.shape[0]):
            slc = model.predict(level_chunks[i])
            model.decode_slice(slc[0], predicted_map, i*model.cols)
        test = FullTileTesting.MapTest(true_map, predicted_map)
        results["errors"].append(test.get_total_tile_errors())
    tend = time.process_time()
    results["test_time"] = tend-tstart
    return results


def write_test_results(hidden_pct, encoded_pct, ohe_batch, bpe_batch, verbose=True):
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
    total_test_time_ohe = 0
    total_train_time_ohe = 0
    total_test_time_bpe = 0

    with open("oheVbpe_raw.csv", "a") as f:
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

            s += str(ohe_batch[i]["test_time"]) + "," + str(bpe_batch[i]["test_time"]) + "\n"
            total_test_time_ohe += ohe_batch[i]["test_time"]
            total_test_time_bpe += bpe_batch[i]["test_time"]
        f.write(s)
        if verbose:
            print(s)

    with open("oheVbpe.csv", "a") as f:
        s = str(hidden_pct) + "," + str(encoded_pct) + ","
        s += str(total_train_time_ohe / num_trials) + "," + str(total_train_time_bpe / num_trials) + ","
        tiles = ohe_batch[0]["tiles"]
        for t in range(num_tests):
            s += str(best_ohe[t] / tiles[t]) + "," + str(best_bpe[t] / tiles[t]) + ","
            s += str(worst_ohe[t] / tiles[t]) + "," + str(worst_bpe[t] / tiles[t]) + ","
            s += str(total_errors_ohe[t] / num_tests / tiles[t]) + ","
            s += str(total_errors_bpe[t] / num_tests / tiles[t]) + ","
        s += str(total_test_time_ohe / num_trials) + "," + str(total_test_time_bpe / num_trials) + "\n"
        f.write(s)
        if verbose:
            print(s)


def perform_comparison_tests():
    for e in range(1, 6):
        for h in range(e+1, 9):
            tf.keras.backend.clear_session()
            ohe_results = []
            bpe_results = []
            for t in range(10):
                print(f"Test for {h/10},{e/10} trial{t}")
                ohe = FullTileTesting.OneHotEncoder(4, 14, h / 10, e / 10, optimizer="adamax", loss="cosine_similarity")
                ohe_results.append(train_and_test(ohe))
                bpe = FullTileTesting.BitplainEncoder(4, 14, h / 10, e / 10, optimizer="adam", loss="mean_squared_error")
                bpe_results.append(train_and_test(bpe))
            write_test_results(h / 10, e / 10, ohe_results, bpe_results)


if __name__ == "__main__":
    perform_comparison_tests()
