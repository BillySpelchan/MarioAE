import numpy as np

from keras.layers import Input, Dense
from keras.models import Model
from keras.models import load_model

from litetux.LTMap import LiteTuxMap, LTSpeedrunStateManager, PathExtractorWithJumpState
from litetux import LTMap

class LTModel:
    def __init__(self):
        self.model_input = None
        self.model_layers = None
        self.model = None
        self.input_size = 0
        #self.create_model()

    def create_model(self, in_lay=108, hidden=54, encode=27, noise=False):
        self.input_size = in_lay
        self.model_input = Input(shape=(in_lay,))
        """
        self.model_layers = Dense(units=hidden, activation="relu")(self.model_input)
        self.model_layers = Dense(units=encode, activation="tanh")(self.model_layers)
        self.model_layers = Dense(units=hidden, activation="relu")(self.model_layers)
        self.model_layers = Dense(units=in_lay, activation="tanh")(self.model_layers)
        """
        self.model_layers = Dense(units=hidden, activation="tanh")(self.model_input)
        self.model_layers = Dense(units=encode, activation="tanh")(self.model_layers)
        self.model_layers = Dense(units=hidden, activation="tanh")(self.model_layers)
        self.model_layers = Dense(units=in_lay, activation="relu")(self.model_layers)
        self.model = Model(self.model_input, self.model_layers)
        self.model.summary()
        #self.model.compile(optimizer='adadelta', loss='binary_crossentropy')
        self.model.compile(optimizer='adadelta', loss='mean_squared_error')
        return self.model

    def train_model(self, training_set, epoch, verbose=0):
        self.model.fit(training_set, training_set, epochs=epoch, verbose=verbose)

    def train_for_different_output(self, in_set, out_set, epoch, verbose=0):
        self.model.fit(in_set, out_set, epochs=epoch, verbose=verbose)

    def predict_slice(self, slc):
        prediction = self.model.predict(slc.reshape((1, self.input_size)), batch_size=1)
        return prediction

    def clean_prediction(self, slc, prediction=None):
        if prediction is None:
            prediction = self.predict_slice(slc)
        cleaned = np.zeros(prediction.shape[1])
        for indx in range(prediction.shape[1]):
            if (prediction[0, indx] > 0):
                cleaned[indx] = 1
        return cleaned

    def save(self, saved_model_name="lt.h5"):
        self.model.save(saved_model_name)

    def load(self, saved_model_name="lt.h5"):
        self.model = load_model(saved_model_name)

class PerformTests:
    def build_strip_set(self, ltmap, cols_in_slice, path_extractor):
        results = None
        if path_extractor is not None:
            extracted_path = path_extractor.perform_extraction()
            if len(extracted_path.shape) == 2:
                extracted_path = np.reshape(extracted_path, (1, extracted_path.shape[0], extracted_path.shape[1]))
            shape = extracted_path.shape
        for i in range(ltmap.width - cols_in_slice):
            strip = ltmap.extract_planes(8, i, cols_in_slice)
            if path_extractor is not None:
                for p in range(shape[0]):
                    for c in range(cols_in_slice):
                        strip = np.append(strip, extracted_path[p,:,i+c])
            strip = np.reshape(strip, (1, strip.shape[0]))
            if results is None:
                results = strip
            else:
                results = np.vstack([results,strip])
        return results

    def build_training_set(self, list, cols_in_slice, extractor_class):
        training_set = None
        ltm = LiteTuxMap(1,1)
        sm = LTSpeedrunStateManager()
        for filename in list:
            print("processing ", filename)
            ltm.load(filename)
            if extractor_class is not None:
                path_extractor = extractor_class(ltm, sm, 0,8)
                path_extractor.perform_extraction()
            else:
                path_extractor = None
            slices = self.build_strip_set(ltm, cols_in_slice, path_extractor)
            if training_set is None:
                training_set = slices
            else:
                training_set = np.vstack([training_set, slices])
        return training_set

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
            # print(orig_strs[col], " | ", der_strs[col], ' | ', end='')
            for row in range(rows):
                result += COMP_LETTERS[comp[indx + rows - row - 1]]
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

    def test_level(self, expected_slices, model, env_bits, test_name):
        shape = expected_slices.shape
        error_count = 0
        solid_error_count = 0
        for i in range(shape[0]):
            prediction = model.predict_slice(expected_slices[i])
            test_result = self.compare_env_encoding(expected_slices[i,0:env_bits], prediction[0, 0:env_bits])
            error_count += self.count_comparison_errors(test_result)
            solid_error_count += self.count_comparison_should_be_solid_errors(test_result)
        return test_name + "," + str(error_count) + "," + str(solid_error_count) +\
                "," + str(error_count/shape[0]) + "," + str(solid_error_count/error_count)

    def test_prediction(self, slices, model, cols_per_slice, test_name):
        shape = slices.shape
        env_bits = cols_per_slice * 14 # TODO refactor out sizes somehow
        error_count = 0
        solid_error_count = 0
        for i in range(shape[0]-cols_per_slice):
            prediction = model.predict_slice(slices[i])
            test_result = self.compare_env_encoding(slices[i+cols_per_slice,0:env_bits], prediction[0, 0:env_bits])
            error_count += self.count_comparison_errors(test_result)
            solid_error_count += self.count_comparison_should_be_solid_errors(test_result)
        return test_name + "," + str(error_count) + "," + str(solid_error_count) +\
                "," + str(error_count/shape[0]) + "," + str(solid_error_count/error_count)


def test_strip_extraction():
    ltm = LiteTuxMap(1, 1)
    ltm.load("levels/mario1-1.json")
    sm = LTSpeedrunStateManager(4, True)
    extractor = PathExtractorWithJumpState(ltm, sm, 0, 11)
    tests = PerformTests()
    strips = tests.build_strip_set(ltm, 2, extractor)
    print(strips.shape)
    for i in range(strips.shape[0]):
        print(strips[i,:])

def perform_baseline_batch_test(training_levels, test_levels, extractor_classes, filename):
    test = PerformTests()
    csv = open(filename, 'w')
    for extractor_class in extractor_classes:
        print("Testing ", extractor_class)
        training_set = test.build_training_set(training_levels, 4, extractor_class)
        model = LTModel()
        model.create_model(training_set.shape[1], training_set.shape[1]//2, training_set.shape[1]//4)
        model.train_model(training_set,training_set.shape[1])
        for name in test_levels:
            test_set = test.build_training_set([name], 4, extractor_class)
            result = test.test_level(test_set, model, 14 * 4, str(extractor_class)+name)
            print(result)
            csv.write(result)
            csv.write("\n")
    csv.close()

def perform_full_batch_test(training_levels, test_levels, extractor_classes, filename):
    test = PerformTests()
    csv = open(filename, 'w')
    eid = 0
    for extractor_class in extractor_classes:
        print("Testing ", extractor_class)
        training_set = test.build_training_set(training_levels, 4, extractor_class)
        input_size = training_set.shape[1]
        step_size = input_size // 10
        for hidden in range (step_size//2, input_size-step_size, step_size):
            for encoding in range (step_size, hidden-step_size, step_size):
                name_base = str(extractor_class)+str(hidden)+"-"+str(encoding)+"," + str(eid)
                model = LTModel()
                model.create_model(input_size, hidden, encoding)
                model.train_model(training_set,input_size)
                mapid = 0
                for name in test_levels:
                    test_set = test.build_training_set([name], 4, extractor_class)
                    result = test.test_level(test_set, model, 14 * 4, name_base+','+str(mapid))
                    print(result)
                    csv.write(result)
                    csv.write("\n")
                    mapid += 1
        eid += 1
    csv.close()


def perform_prediction_batch_test(training_levels, test_levels, extractor_classes, filename):
    test = PerformTests()
    csv = open(filename, 'w')
    for extractor_class in extractor_classes:
        print("Testing ", extractor_class)
        training_set = test.build_training_set(training_levels, 4, extractor_class)
        model = LTModel()
        model.create_model(training_set.shape[1], training_set.shape[1]//2, training_set.shape[1]//4)
        n = training_set.shape[0]
        model.train_for_different_output(training_set[:n-4,:], training_set[4:,:],150)
        for name in test_levels:
            test_set = test.build_training_set([name], 4, extractor_class)
            result = test.test_prediction(test_set, model, 4, str(extractor_class)+name)
            print(result)
            csv.write(result)
            csv.write("\n")
    csv.close()

def perform_full_prediction_test(training_levels, test_levels, extractor_classes, filename):
    test = PerformTests()
    csv = open(filename, 'w')
    eid = 0
    for extractor_class in extractor_classes:
        print("Testing ", extractor_class)
        training_set = test.build_training_set(training_levels, 4, extractor_class)
        input_size = training_set.shape[1]
        step_size = input_size // 10
        for hidden in range (step_size//2, input_size-step_size, step_size):
            for encoding in range (step_size, hidden-step_size, step_size):
                name_base = str(extractor_class)+str(hidden)+"-"+str(encoding)+"," + str(eid)
                model = LTModel()
                model.create_model(input_size, hidden, encoding)
                model.train_for_different_output(training_set[:training_set.shape[0] - 4, :], training_set[4:, :], 150)
                model.train_model(training_set,input_size)
                mapid = 0
                for name in test_levels:
                    test_set = test.build_training_set([name], 4, extractor_class)
                    result = test.test_prediction(test_set, model, 4, name_base+','+str(mapid))
                    print(result)
                    csv.write(result)
                    csv.write("\n")
                    mapid += 1
        eid += 1
    csv.close()

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
    """
    tests = PerformTests()
    strips = tests.build_training_set(TRAIN_LEVELS, 4, LTMap.BasicExtractor)
    print(strips.shape)
    model = LTModel()
    model.create_model(8*14,4*14,2*14)
    model.train_model(strips, 50)
    prediction = model.predict_slice(strips[0])
    print(prediction)
    results = tests.compare_env_encoding_to_col_string(strips[0], prediction[0], 14)
    print(results)
    test_strips = tests.build_training_set([TEST_LEVELS[0]],4, LTMap.BasicExtractor)
    print(tests.test_level(test_strips, model, 14*4, "test"))
    """
    #perform_baseline_batch_test(TRAIN_LEVELS, TEST_LEVELS, EXTRACTORS, "path_test_bv2.csv")
    #perform_full_batch_test(TRAIN_LEVELS, TEST_LEVELS, EXTRACTORS, "path_test2.csv")
    #perform_prediction_batch_test(TRAIN_LEVELS, TEST_LEVELS, EXTRACTORS, "predict_base2.csv")
    perform_full_prediction_test(TRAIN_LEVELS, TEST_LEVELS, EXTRACTORS, "predict_full.csv")
