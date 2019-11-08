# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 13:51:15 2019

@author: Billy D. Spelchan
"""
import numpy as np

from keras.layers import Input, Dense
from keras.models import Model
from keras.models import load_model

class MarioModel:
    def __init__(self):
        self.model_input = None
        self.model_layers = None
        self.model = None
        self.create_model()

    def create_model(self, in_lay = 56, hidden = 28, encode = 14, noise=False):
        self.model_input = Input(shape=(in_lay,))
        self.model_layers = Dense(units=hidden, activation="relu")(self.model_input)
        self.model_layers = Dense(units=encode, activation="tanh")(self.model_layers)
        self.model_layers = Dense(units=hidden, activation="relu")(self.model_layers)
        self.model_layers = Dense(units=in_lay, activation="relu")(self.model_layers)
        self.model = Model(self.model_input, self.model_layers)
        self.model.summary()
        self.model.compile(optimizer='adadelta', loss='binary_crossentropy')
        return self.model
    
    def train_model(self, training_set, epoch ):
        self.model.fit(training_set, training_set, epochs=epoch)
    
    def predict_slice(self, slc):
        prediction = self.model.predict(slc.reshape((1,56)), batch_size=1)
        return prediction

    def save(self, saved_model_name="mario.h5"):
        self.model.save(saved_model_name)
    
    def load(self, saved_model_name="mario.h5"):
        self.model = load_model(saved_model_name)
