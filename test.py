import pickle
import time
import os
import numpy as np
import environment
import random
import os

PATH = os.path.abspath("..\\..\\qtables") + "/" + "table" + str(4) + "/"


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



print(qtableread("0222102210221021"))
