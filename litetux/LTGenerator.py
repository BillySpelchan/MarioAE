from litetux import LTMap, LTModel, FullTileTesting
import numpy as np
import random

class LTMapGenerator():
    def __init__(self, model=None, cleaner=None, slice_cols=4, slice_rows=14):
        self.map = None
        self.model = model
        if model is None:
            self.model = FullTileTesting.BitplainEncoder(slice_cols,slice_rows)
        self.cleaner = cleaner
        if cleaner is None:
            self.cleaner = FullTileTesting.BitplainEncoder(slice_cols, slice_rows)
        self.tester = LTModel.PerformTests()
        self.cols_in_slice = 4
        self.start_slice = self.model.encode_slice

    def get_input_output_sets_for_model(self, level_list):
        ltm = LTMap.LiteTuxMap(1, 1)
        step_size = self.model.cols
        in_set = None
        out_set = None
        for lvl in level_list:
            ltm.load(lvl)
            slice_set = None
            end_col = ltm.width - self.model.cols
            for c in range(0, end_col, step_size):
                if slice_set is None:
                    slice_set = np.reshape(self.model.encode_slice(ltm, c), (1, self.model.in_nodes))
                else:
                    slice_set = np.vstack([slice_set, np.reshape(self.model.encode_slice(ltm, c), (1, self.model.in_nodes))])
            if in_set is None:
                in_set = slice_set[0:-1, :]
                out_set = slice_set[1:, :]
            else:
                in_set = np.vstack([in_set, slice_set[0:-1, :]])
                out_set = np.vstack([out_set, slice_set[1:, :]])

        return (in_set, out_set)

    def train_models(self, training_levels, epochs = 300):
        train_in, train_out = self.get_input_output_sets_for_model(training_levels)
        self.start_slice = train_in[0,:]
        self.model.train(train_in, train_out, epochs)
        clean_in = self.cleaner.build_slice_set(training_levels)
        self.cleaner.train(clean_in, epoch=epochs)

    def build_map(self, cols, noise=0.1, clean=True):
        # TODO handle None start slice
        predicted_map = LTMap.LiteTuxMap(cols, self.model.rows)
        prediction = self.model.predict(self.start_slice)
        cur_col = 0
        while (cur_col < cols):
            #print(self.tester.compare_env_encoding_to_col_string(prediction[0], prediction[0], int(prediction.shape[1]//self.cols_in_slice)))
            for i in range(prediction.shape[1]):
                if random.random() < noise:
                    prediction[0,i] = 1 if prediction[0,1] < .5 else 0
            prediction = self.model.predict(prediction)
            if clean:
                prediction = self.cleaner.predict(prediction)
            self.model.decode_slice(prediction[0], predicted_map, cur_col)
            cur_col += self.cols_in_slice
        print(predicted_map.to_vertical_string())
        return predicted_map


TRAIN_LEVELS = ["levels/mario-1-1.json",
              "levels/mario-2-1.json","levels/mario-3-1.json",
              "levels/mario-4-1.json","levels/mario-4-2.json","levels/mario-5-1.json",
              "levels/mario-6-1.json","levels/mario-6-2.json",
              "levels/mario-7-1.json","levels/mario-8-1.json"]
TEST_LEVELS = ["levels/mario-1-2.json", "levels/mario-3-3.json", "levels/mario-6-1.json"]

EXTRACTORS = [None, LTMap.BasicExtractor, LTMap.BestReachableAsBitsExtractor,
              LTMap.LastInColumnPathExtractor, LTMap.BestReachableAsFloatExtractor,
              LTMap.PathExtractor, LTMap.PathExtractorWithJumpState]

if __name__ == "__main__":
    size = input("Map size: ")
    noise = input("Noise (0-1.0): ")
    cleanStr = input("Clean (Y/N): ")
    clean = True if cleanStr.startswith("y") or cleanStr.startswith("Y") else False
    gen = LTMapGenerator()
    gen.train_models(TRAIN_LEVELS)
    level = gen.build_map(int(size), float(noise), clean)
    should_save = input("Save map? ")
    if should_save.startswith("y") or should_save.startswith("Y"):
        filename = input("filename: ")
        level.save(filename)
