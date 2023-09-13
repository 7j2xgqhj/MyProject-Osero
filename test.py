import pickle
import time
import os
import numpy as np
import environment
import random
import os

SIZE = 4
PATH = os.path.abspath("..\\..\\qtables") + "/" + "table" + str(SIZE) + "/"


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


st = "1234567891234567"
a = [st[12 * i:12 * (i + 1)] + "/" for i in range(int((SIZE*SIZE-1)/12))]
print(a)
