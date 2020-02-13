# -*- coding: utf-8 -*-
"""
Created on Tue Dec 17 09:18:40 2019

@author: spelc
"""


import numpy as np

from keras.layers import Input, Dense
from keras.models import Model
from keras.models import load_model

import stparser

class STModel:
    def __init__(self):
        self.model_input = None
        self.model_layers = None
        self.model = None
        self.input_size = 0
        self.create_model()

    def create_model(self, in_lay = 108, hidden = 54, encode = 27, noise=False):
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
    
    def train_model(self, training_set, epoch ):
        self.model.fit(training_set, training_set, epochs=epoch)
        
    def train_for_different_output(self, in_set, out_set, epoch):
        self.model.fit(in_set, out_set, epochs=epoch)
    
    def predict_slice(self, slc):
        prediction = self.model.predict(slc.reshape((1,self.input_size)), batch_size=1)
        return prediction

    def clean_prediction(self, slc, prediction = None):
        if prediction is None:
            prediction = self.predict_slice(slc)
        cleaned = np.zeros(prediction.shape[1])
        for indx in range(prediction.shape[1]):
            if (prediction[0,indx] > 0):
                cleaned[indx] = 1
        return cleaned
        
    def save(self, saved_model_name="st.h5"):
        self.model.save(saved_model_name)
    
    def load(self, saved_model_name="st.h5"):
        self.model = load_model(saved_model_name)

def print_slice_as_grid(slc, width, height):
    indx = 0
    for r in range(height):
        for c in range(width):
            ch = '.' if slc[indx] == 0 else '*'
            print(ch, end='')
            indx += 1
        print()
        
def get_training_set(lvl, width, start, end):
    slices = None
    for c in range(start, end-width):
        slc = lvl.get_slice(c, width)
        if slices is None:
            slices = slc.reshape((1, width*27))
        else:
            slices = np.append(slices, slc.reshape((1, width*27)), axis=0 )
    return slices

    
# TODO - Move to separte test module once stablized
if __name__ == "__main__":
    level = stparser.STLevel("tuxlevels/icy_valley.stl")
    #level.get_slice(0, 512)
    training = get_training_set(level, 4, 4, 512)
    model = STModel()
    model.create_model()
    model.train_model(training, 200)
    predict = model.predict_slice(training[0])
    print_slice_as_grid(training[0], 4,27)
    print("---------------")
    print_slice_as_grid(model.clean_prediction(predict), 4,27)

