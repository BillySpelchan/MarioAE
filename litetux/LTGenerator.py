from litetux import LTMap, LTModel
import random

class LTMapGenerator():
    def __init__(self):
        self.map = None
        self.model = None
        self.cleaner = None
        self.tester = LTModel.PerformTests()
        self.cols_in_slice = 4
        self.start_slice = None

    def create_model(self, training, cols_in_slice, hidden=-1, encode=-1, epoch=150):
        training_set = self.tester.build_training_set(training, cols_in_slice, None)

        self.cols_in_slice = cols_in_slice
        n = training_set.shape[0]
        self.start_slice = training_set[0]
        self.model = LTModel.LTModel()
        hl = hidden if hidden > 0 else training_set.shape[1]//2
        el = encode if encode > 0 else training_set.shape[1]//4
        self.model.create_model(training_set.shape[1], hl, el)
        self.model.train_for_different_output(training_set[:n-cols_in_slice,:], training_set[cols_in_slice:,:],epoch)

        self.cleaner = LTModel.LTModel()
        self.cleaner.create_model(training_set.shape[1], hl, el)
        self.cleaner.train_model(training_set,epoch)

    def build_map(self, cols, noise = .1, clean = True):
        prediction = self.model.predict_slice(self.start_slice)
        cur_col = 0
        while (cur_col < cols):
            cur_col += self.cols_in_slice
            print(self.tester.compare_env_encoding_to_col_string(prediction[0], prediction[0], int(prediction.shape[1]//self.cols_in_slice)))
            for i in range(prediction.shape[1]):
                if random.random() < noise:
                    prediction[0,i] = 1 if prediction[0,1] < .5 else 0
            prediction = self.model.predict_slice(prediction)
            if clean:
                prediction = self.cleaner.predict_slice(prediction)


TRAIN_LEVELS = ["levels/mario-1-1.json",
              "levels/mario-2-1.json","levels/mario-3-1.json",
              "levels/mario-4-1.json","levels/mario-4-2.json","levels/mario-5-1.json",
              "levels/mario-6-1.json","levels/mario-6-2.json",
              "levels/mario-7-1.json","levels/mario-8-1.json"]
TEST_LEVELS = ["levels/mario-1-2.json", "levels/mario-3-3.json", "levels/mario-6-1.json"]

EXTRACTORS = [None, LTMap.BasicExtractor, LTMap.BestReachableAsBitsExtractor,
              LTMap.LastInColumnPathExtractor, LTMap.BestReachableAsFloatExtractor,
              LTMap.PathExtractor, LTMap.PathExtractorWithJumpState]

gen = LTMapGenerator()
gen.create_model(TRAIN_LEVELS, 4)
gen.build_map(80)
