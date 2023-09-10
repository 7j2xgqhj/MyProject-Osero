import pickle
import time
import os
import numpy as np
import environment
import random
import os

NUM = 8
PATH = os.path.abspath("..\\..\\qtables") + "/" + "table" + str(NUM) + "/"


def qtableread(filename: str):
    if os.path.isfile(PATH + "a" + filename + ".pkl"):
        with open(PATH + "a" + filename + ".pkl", 'rb') as f:
            data = pickle.load(f)
        return data
    else:
        return


def qtablesave(filename: str, obj: dict):
    with open(PATH + "a" + filename + ".pkl", 'wb') as f:
        pickle.dump(obj, f)


def res(path, count):
    if count != NUM * NUM - 12:
        c = count + 1
        for i in [0, 1, 2]:
            fp = path + str(i) + "/"
            os.mkdir(fp)
            res(fp, c)


res(PATH + "b/", 0)
res(PATH + "w/", 0)