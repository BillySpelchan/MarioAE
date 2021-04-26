# Importing the libraries
import numpy as np
import random

# Importing the Keras libraries
from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.layers import LSTM
from keras.layers import Dropout

# import matplotlib.pyplot as plt
# import pandas as pd

TILES = "-oES?Q<>[]X"
TILE_EMPTY = 0
TILE_COIN = 1
TILE_ENEMY = 2
TILE_BREAKABLE = 3
TILE_QUESTION = 4
TILE_POWERUP = 5
TILE_LEFT_PIPE = 6
TILE_RIGHT_PIPE = 7
TILE_LEFT_PIPE_TOP = 8
TILE_RIGHT_PIPE_TOP = 9
TILE_BRICK = 10

ACTION_NONE = 0
ACTION_MOVING = 1
ACTION_JUMP1 = 2
ACTION_JUMP2 = 4
ACTION_JUMP3 = 8
ACTION_FALLING = 16


class Path_info:
    def __init__(self, level, mario_start_x, mario_start_y):
        self.source_level = level
        self.num_rows = level.shape[0]
        self.num_cols = level.shape[1]
        print("level size is ", self.num_rows, self.num_cols)
        self.path_info = np.zeros((3, self.num_rows, self.num_cols))
        self.path_info[0, :, :] = level[:, :]
        self.path_info[1, mario_start_y, mario_start_x] = 1  # start position has walking action
        self.find_paths(mario_start_x, mario_start_y)
        self.tile_counts = None

    def find_paths(self, mario_start_x, mario_start_y):
        end_x = self.num_cols
        for col in range(mario_start_x + 1, end_x):
            freefall = False
            for row in range(0, 13):  # bottom row is death so ...
                if self.path_info[0, row, col] < 2:  # if player can enter tile
                    state = 0
                    if (int(self.path_info[1, row, col - 1]) & 1) == 1:
                        if self.path_info[0, row + 1, col] < 2:
                            freefall = True
                    t = int(self.path_info[1, row + 1, col - 1])
                    if (t & 1) == 1: state = state | 2
                    if (t & 2) == 2: state = state | 4
                    if (t & 4) == 4: state = state | 8
                    if (t & 8) == 8: freefall = True
                    if (row < 12):
                        t = int(self.path_info[1, row + 2, col - 1])
                        if (t & 1) == 1: state = state | 4
                        if (t & 2) == 2: state = state | 8
                        if (t & 4) == 4: freefall = True
                    if (row < 11):
                        t = int(self.path_info[1, row + 3, col - 1])
                        if (t & 1) == 1: state = state | 8
                        if (t & 2) == 2: freefall = True
                    if (row < 10):
                        t = int(self.path_info[1, row + 3, col - 1])
                        if (t & 1) == 1: freefall = True
                    if (row > 0):
                        t = int(self.path_info[1, row - 1, col - 1])
                        if t > 0: freefall = True
                    if (freefall):
                        if (self.path_info[0, row + 1, col] > 1):
                            state = state | 1
                            freefall = False
                        else:
                            state = state | 16
                    self.path_info[1, row, col] = state
            print(path_column_to_string(self.path_info, col), self.is_column_a_gap(col),
                  self.is_column_an_obstacle(col))

    def count_tile_usage(self):
        if self.tile_counts is None:
            self.tile_counts = np.zeros((11))
        for row in range(0, self.num_rows):
            for col in range(0, self.num_cols):
                self.tile_counts[int(self.path_info[0, row, col])] += 1
        for count in self.tile_counts:
            print(count)

    def is_completable(self):
        completable = False
        for row in range(0, self.num_rows):
            if self.path_info[1, row, self.num_cols - 1] > 0:
                completable = True
                break
        return completable

    def num_empty_tiles(self):
        if self.tile_counts is None: self.count_tile_usage()
        return self.tile_counts[0]

    def num_reachable_tiles(self):
        reachable_count = 0
        for col in range(0, self.num_cols):
            for row in range(0, 13):
                if (self.path_info[1, row, col] > 0):
                    reachable_count += 1
        return reachable_count

    def num_interesting_tiles(self):
        if self.tile_counts is None: self.count_tile_usage()
        interesting_count = 0
        for tile_type in range(TILE_ENEMY, TILE_BRICK):
            interesting_count += self.tile_counts[tile_type]
        return interesting_count

    def is_column_a_gap(self, col):
        gap = self.path_info[0, self.num_rows - 1, col] == TILE_EMPTY
        return gap

    def is_column_an_obstacle(self, col):
        if (col == 0): return False
        lowest_path = 0;
        for row in range(1, self.num_rows):
            if (int(self.path_info[1, row, col]) & ACTION_MOVING) > 0:
                lowest_path = row
        if (int(self.path_info[1, lowest_path, col - 1]) & ACTION_MOVING) > 0:
            return False
        return True

    def calculate_leniency(self):
        if self.tile_counts is None: self.count_tile_usage()
        # the number of enemies plus the number of gaps minus the number of rewards.
        enemy_count = self.tile_counts[TILE_ENEMY]
        reward_count = self.tile_counts[TILE_COIN] + \
                       self.tile_counts[TILE_POWERUP] + \
                       self.tile_counts[TILE_QUESTION]
        gap_count = 0
        for col in range(2, self.num_cols):
            if self.is_column_a_gap(col): gap_count += 1
        return enemy_count + gap_count - reward_count

    def number_of_potential_jumps(self):
        return 0

    def number_of_required_jumps(self):
        return 0

    def print_test_results(self):
        print("Completable: ", self.is_completable())
        print("Empty tiles: ", self.num_empty_tiles())
        print("Reachable Tiles: ", self.num_reachable_tiles())
        print("Interesting Tiles: ", self.num_interesting_tiles())
        print("Leniency: ", self.calculate_leniency())
        print("Number of potential jumps: ", self.number_of_required_jumps())
        print("Number of required jumps: ", self.number_of_required_jumps())


def load_level(level_name):
    f = open(level_name, "r")
    raw_level = f.readlines()
    f.close()
    # print(raw_level)
    num_cols = len(raw_level[0]) - 1
    print("Debug - level columns = ", num_cols)

    level_data = np.zeros((14, num_cols))
    for row in range(0, 14):
        for col in range(0, num_cols):
            tile = TILES.index(raw_level[row][col])
            # todo error correction for invalid tiles
            level_data[row][col] = tile;
    return level_data


def path_column_to_string(path_info, col):
    s = ""
    for row in range(0, 14):
        if (path_info[1, 13 - row, col] != 0):
            if path_info[0, 13 - row, col] < 2:
                s = s + '*'
            else:
                s = s + 'invalid'
        else:
            s = s + TILES[int(path_info[0, 13 - row, col])]
    return s


def is_tile_empty(level, x, y):
    if y > 13:
        return True
    if (level[y, x] < 2):
        return True
    return False;


"""
Simple method to take level segment and convert it into the input necessary
for the neural network.
"""


def grab_inputs_from_level(level, x, y, size):
    tx = x
    ty = y
    data = np.zeros((size, len(TILES)))
    for t in range(0, size):
        tile = level[ty][tx]
        data[t][int(tile)] = 1
        ty -= 1
        if (ty < 0):
            ty = 13
            tx += 1
    return data


def turn_output_into_tile(array, byRandom=False):
    if byRandom:
        weight = random.random()
        picked = 0
        indx = 0
        while (weight > 0) and (indx < len(TILES)):
            if weight <= array[indx]:
                picked = indx
                weight = 0
            else:
                weight -= array[indx]
                indx += 1
    else:
        picked = 0
        for indx in range(1, len(array)):
            if array[indx] > array[picked]:
                picked = indx
    return picked


def build_training_set(level, start_col, end_col, chunk_size):
    true_end = end_col - int(chunk_size / 14)
    if (true_end <= start_col):
        true_end = start_col + 1
    num_tests = (true_end - start_col) * 14
    training = np.zeros((num_tests, chunk_size, len(TILES)))
    results = np.zeros((num_tests, len(TILES)))
    test_id = 0
    for x in range(start_col, true_end):
        for y in range(0, 14):
            temp = grab_inputs_from_level(level, x, y, chunk_size + 1)
            training[test_id] = temp[0:chunk_size, :]
            results[test_id] = temp[chunk_size]
            test_id += 1
    return training, results


def build_simple_model(dropout=0):
    model = Sequential()
    # input layer and first (only in this model)
    model.add(LSTM(units=200, return_sequences=False, input_shape=(200, len(TILES))))
    if (dropout > 0):
        model.add(Dropout(dropout))
    # ouput layers
    model.add(Dense(units=len(TILES)))
    model.add(Activation("softmax"))
    model.compile(loss="categorical_crossentropy", optimizer="rmsprop")
    return model


def coordinate_to_string_position(x, y, snaking=False, offset=0):
    ty = y
    if snaking and (x % 2 == 1):
        ty = 13 - y
    p = x * 14 + ty + offset
    return p


def string_position_to_coordinate(pos, snaking=False):
    x = pos // 14
    y = pos % 14
    if snaking and (x % 2 == 1):
        y = 13 - y
    return x, y


def testing():
    for t in range(200):
        x, y = string_position_to_coordinate(t)
        n = coordinate_to_string_position(x, y)
        if n != t:
            print("Problem with coordinate/position conversion non-snaking")
            print(x, y, n)
    for t in range(200):
        x, y = string_position_to_coordinate(t, True)
        n = coordinate_to_string_position(x, y, True)
        if n != t:
            print("Problem with coordinate/position conversion non-snaking")
            print(x, y, n)


'''
only the first seed_size tiles of the seeding level are used

def build_level_with_model(model, seeding_level, seed_size, columns):
'''

level = load_level("../levels/mario-1-1.txt")
path = Path_info(level, 1, 12)
path.count_tile_usage()
path.print_test_results()


for r in range(1 , 40):
    data = grab_inputs_from_level(level, r, 13, 14)
    print(data)
    s= ""
    for i in range(0, 14):
        s = s + TILES[turn_output_into_tile(data[i])]
    print(s)
training, results = build_training_set(level, 0, 100, 200)
print(training)
print(results)
print("creating model")
model = build_simple_model()
print("training")
print("train dim = ", training.shape)
test = training[0:0,:,:]
print("train dim = ", test.shape)
model.fit(training, results, batch_size=32, epochs=1)
print("predicting")
prediction = model.predict(training[0:1,:,:])
print(prediction)


'''
testing()
'''