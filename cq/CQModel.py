# -*- coding: utf-8 -*-
"""
Created on Thu Nov 28 20:53:49 2019

@author: spelc
"""

import numpy as np

from keras.layers import Input, Dense
from keras.models import Model
from keras.models import load_model

import CQMap

class CQModel:
    def __init__(self):
        self.model_input = None
        self.model_layers = None
        self.model = None
        self.create_model()

    def create_model(self, in_lay = 49, hidden = 25, encode = 12, noise=False):
        self.model_input = Input(shape=(in_lay,))
        self.model_layers = Dense(units=hidden, activation="relu")(self.model_input)
        self.model_layers = Dense(units=encode, activation="tanh")(self.model_layers)
        self.model_layers = Dense(units=hidden, activation="relu")(self.model_layers)
        self.model_layers = Dense(units=in_lay, activation="tanh")(self.model_layers)
        self.model = Model(self.model_input, self.model_layers)
        self.model.summary()
        self.model.compile(optimizer='adadelta', loss='binary_crossentropy')
        return self.model
    
    def train_model(self, training_set, epoch ):
        self.model.fit(training_set, training_set, epochs=epoch)
    
    def predict_slice(self, slc):
        prediction = self.model.predict(slc.reshape((1,49)), batch_size=1)
        return prediction

    def clean_prediction(self, prediction = None):
        if prediction is None:
            prediction = self.predict_slice()
        cleaned = np.zeros(prediction.shape[1])
        for indx in range(prediction.shape[1]):
            if (prediction[0,indx] > 0):
                cleaned[indx] = 1
        return cleaned
        
    def save(self, saved_model_name="cq.h5"):
        self.model.save(saved_model_name)
    
    def load(self, saved_model_name="cq.h5"):
        self.model = load_model(saved_model_name)

def print_slice_as_grid(slc, width, height):
    indx = 0
    for r in range(height):
        for c in range(width):
            ch = '.' if slc[indx] == 0 else '*'
            print(ch, end='')
            indx += 1
        print()
        
    
# TODO - Move to separte test module once stablized
if __name__ == "__main__":
    cqmap = CQMap.CQMap()
    raw = cqmap.load_cq2txt("../levels/cq/icemaze.txt")
    train = cqmap.get_is_solid_training_set(7,7)
    print(train)
    model = CQModel()
    model.create_model()
    model.train_model(train, 200)
    predict = model.predict_slice(train[0])
    print_slice_as_grid(train[0], 7,7)
    print("---------------")
    print_slice_as_grid(model.clean_prediction(predict), 7,7)

