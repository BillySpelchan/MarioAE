# -*- coding: utf-8 -*-
"""
Created on Thu Nov 28 09:00:19 2019

@author: spelc
"""
import numpy as np
from tkinter import *

class CQMap:
    BASE64ENC = "-+abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    CQ2_TILES = [1,2,3,4,5,6,7,8,9,10,11,12,55,59,63,78, 78,17,18,19,20,25,27,28,37,40,29,30,1,1,1,1]
    SOLID_TILES_START = 53
    
    def __init__(self):
        self.raw_map = None

    """ loads a CSV file assuming that the file is valid. 
        TODO Should have Error checking """
    def load_csv(self, filename):
        rows = []
        num_cols = 0
        f = open(filename, "r")
        for line in f:
            tiles = line.split(',')
            if len(tiles) > 3: 
                row = np.zeros(len(tiles), dtype=np.int32)
                for indx in range(len(tiles)):
                    row[indx] = int(tiles[indx])
                if len(tiles) > num_cols:
                    num_cols = len(tiles)
                rows.append(row)
        f.close()
        self.raw_map = np.zeros((len(rows), num_cols), dtype=np.int32)
        for row in range(len(rows)):
            for col in range(rows[row].shape[0]):
                self.raw_map[row, col] = rows[row][col]
        return self.raw_map

    def save_csv(self, filename):
        f = open(filename, "w")
        for row in range(self.raw_map.shape[0]):
            for col in range(self.raw_map.shape[1]-1):
                f.write(str(self.raw_map[row,col]))
                f.write(', ')
            f.write(str(self.raw_map[row,self.raw_map.shape[1]-1]))
            f.write("\n")
        f.close()

        
    """ loads a CQ1 or CQ2 text file assuming that the file is valid. 
        TODO Should have Error checking """
    def load_cq2txt(self, filename):
        f = open(filename, "r")
        line = f.readline()
        num_cols = int(f.readline())
        self.raw_map = np.zeros((num_cols, num_cols), dtype=np.int32)
        for row in range(num_cols):
            line = f.readline()
            for col in range(num_cols):
                self.raw_map[row, col] = CQMap.CQ2_TILES[CQMap.BASE64ENC.index(line[col])]
        f.close()
        return self.raw_map

    """ for nn manipulation want to have bits of the level that are solid
        or empty so the slice is created and will be a 1d strip of tiles
        layed out with rows appended to each other """
    def get_is_solid_slice(self, col, row, width, height):
        slc = np.zeros((width*height))
        indx = 0
        for r in range(height):
            for c in range(width):
                slc[indx] = 1 if self.raw_map[row+r, col+c] >= CQMap.SOLID_TILES_START else 0
                indx += 1
        return slc

    def get_is_solid_training_set(self, width, height):
        shape = self.raw_map.shape
        slices = None
        for c in range(1, shape[1]-width):
            for r in range(1, shape[0]-height):
                slc = self.get_is_solid_slice(c, r, width, height)
                if slices is None:
                    slices = slc.reshape((1, width*height))
                else:
                    slices = np.append(slices, slc.reshape((1, width*height)), axis=0 )
        return slices

# TODO - Move to separte test module once stablized
if __name__ == "__main__":
    cqmap = CQMap()
    raw = cqmap.load_csv("../levels/cq/cq1b1.csv")
    print(raw)
    raw = cqmap.load_cq2txt("../levels/cq/icemaze.txt")
    print(raw)
    #cqmap.save_csv("../levels/cq/icemaze.csv")
    #slc = cqmap.get_is_solid_slice(4,2, 7,7)
    #print(slc)
    train = cqmap.get_is_solid_training_set(7,7)
    print(train)