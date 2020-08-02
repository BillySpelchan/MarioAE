import numpy as np

from keras.layers import Input, Dense
from keras.models import Model
from keras.models import load_model

import stparser


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
        self.model_layers = Dense(units=hidden, activation="relu")(self.model_input)
        self.model_layers = Dense(units=encode, activation="tanh")(self.model_layers)
        self.model_layers = Dense(units=hidden, activation="relu")(self.model_layers)
        self.model_layers = Dense(units=in_lay, activation="tanh")(self.model_layers)
        self.model = Model(self.model_input, self.model_layers)
        self.model.summary()
        self.model.compile(optimizer='adadelta', loss='binary_crossentropy')
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
    def buildTrainingData(self, ltmap, cols_in_slice, path_extractor):

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
