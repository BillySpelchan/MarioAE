import random

import keras
import numpy as np
from tensorflow.python.keras.layers import RNN

from litetux import LTMap, FullTileTesting
# Importing the Keras libraries
from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.layers import LSTM
from keras.layers import Dropout
import tensorflow as tf
import os.path

class LiteTuxOHE:
    def __init__(self, memory_size=200, verbose=False):
        self.model = None
        self.verbose = verbose
        self.memory_size = memory_size
        self.rnd = random.Random()

    def log(self, string):
        if (self.verbose):
            print(string)

    def map_to_training_set(self, lvl):
        total_tiles = lvl.width * lvl.height
        slices = np.zeros((total_tiles-self.memory_size, self.memory_size, 16))
        results = np.zeros((total_tiles-self.memory_size, 16))
        for i in range(total_tiles-self.memory_size):
            for offset in range(self.memory_size):
                index = i+offset
                t = max(0,min(15,lvl.get_tile(index//lvl.height,index%lvl.height)))
                slices[i,offset,t] = 1
            index = i+self.memory_size
            t = max(0,min(15,lvl.get_tile(index//lvl.height,index%lvl.height)))
            results[i, t] = 1
        return slices, results

    def load_map_file_as_training_set(self, filename):
        lvl = LTMap.LiteTuxMap()
        lvl.load(filename)
        self.log(lvl.to_vertical_string())
        return self.map_to_training_set(lvl)

    def prediction_to_tile(self, prediction):
        high = prediction[0,0]
        tid = 0
        for i in range(1,16):
            if (prediction[0,i] >= high):
                high = prediction[0,i]
                tid = i
        return tid

    def build_simple_model(self, dropout=0):
        model = Sequential()
        # input layer and first (only in this model)
        model.add(LSTM(units=self.memory_size, return_sequences=False, input_shape=(self.memory_size, 16)))
        if (dropout > 0):
            model.add(Dropout(dropout))
        # ouput layers
        model.add(Dense(units=16))
        model.add(Activation("softmax"))
        model.compile(loss="categorical_crossentropy", optimizer="rmsprop")
        return model

    def build_deep_model(self, dropout=0):
        model = Sequential()
        # input layer and first (only in this model)
        model.add(keras.Input(shape=(self.memory_size,16),batch_size=1))
        model.add(LSTM(units=self.memory_size, return_sequences=True, input_shape=(self.memory_size, 16)))
        if (dropout > 0):
            model.add(Dropout(dropout))
        model.add(LSTM(units=200, return_sequences=True, input_shape=(self.memory_size, 16)))
        model.add(LSTM(units=200, return_sequences=False, input_shape=(self.memory_size, 16)))
        # ouput layers
        model.add(Dense(units=16, activation="softmax"))
        model.compile(loss="mean_squared_error", optimizer="adamax")
        self.model = model
        return model

    def predict_map(self, lvl):
        x,y = self.map_to_training_set(lvl)
        predicted_map = LTMap.LiteTuxMap(lvl.width, lvl.height)
        for i in range(self.memory_size):
            predicted_map.set_tile(i//lvl.height,i%lvl.height, lvl.get_tile(i//lvl.height,i%lvl.height))
        offset = self.memory_size
        for i in range(x.shape[0]):
            pred = model.predict(x[i:i+1, :, :])
            predicted_map.set_tile(offset // lvl.height, offset % lvl.height, self.prediction_to_tile(pred))
            offset += 1
        return predicted_map

    def generate_noisy_tile(self, prediction, noise_level=.01):
        total_weight = 0
        for i in range(16):
            noise = self.rnd.random() * noise_level
            prediction[0,i] += noise
            total_weight += prediction[0,i]
        weight = self.rnd.random() * total_weight
        tid = 0
        while (weight > prediction[0,tid]):
            weight -= prediction[0, tid]
            tid += 1
        if tid > 15:
            tid = 15
        return tid

    def generate_map(self, cols, seedmap):
        tiles_in_map = seedmap.height * cols
        x,y = self.map_to_training_set(seedmap)
        predicted_map = LTMap.LiteTuxMap(cols, seedmap.height)
        for i in range(self.memory_size):
            predicted_map.set_tile(i//seedmap.height,i%seedmap.height,
                                   seedmap.get_tile(i//seedmap.height,i%seedmap.height))
        p = x[0:1, :, :]
        for i in range(self.memory_size, tiles_in_map):
            pred = model.predict(p)
            tid = self.generate_noisy_tile(pred)
            predicted_map.set_tile(i // seedmap.height, i % seedmap.height, tid)
            p = np.roll(p,-16)
            for b in range(16):
                p[0,self.memory_size-1,b] = 1 if b == tid else 0
        return predicted_map

test = LiteTuxOHE(verbose=True)
#build model if we don't have one saved

gpu_devices = tf.config.experimental.list_physical_devices('GPU')
for device in gpu_devices: tf.config.experimental.set_memory_growth(device, True)
#model = test.build_simple_model()
model = test.build_deep_model()
if os.path.isfile("ohe_lstm.h5"):
    model = keras.models.load_model("ohe_lstm.h5")
    test.model = model
else :
    x, y = test.load_map_file_as_training_set("../litetux/levels/lt-2.json")
    model.fit(x,y,epochs=200,batch_size=1)
    model.save("ohe_lstm.h5")
    test.log("saved model")
test_map = LTMap.LiteTuxMap()
test_map.load("../litetux/levels/lt-1.json")
#pred_map = test.predict_map(test_map)
pred_map = test.generate_map(100,test_map)
print(pred_map.to_vertical_string())
pred_map.save("test.json")

'''    
for slc in range(x.shape[0]):
    pred = model.predict(x[slc:slc+1, :, :])
    print(slc, test.prediction_to_tile(y[slc:slc+1,:]), test.prediction_to_tile(pred))
'''