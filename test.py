import pickle
import time
import os
import numpy as np
import environment
import random

PATH = "test/"


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


nn = 5

n = str(int(random.random() * (10 ** nn)))
qtablesave(n, {"[1,2]": [1, 2]})
s = time.perf_counter()
a = qtableread(n)
e = time.perf_counter()
print(a)
print(e - s)
for i in range(10 ** nn):
    qtablesave(str(i), {"[1,2]": [1, 2]})
n = str(int(random.random() * (10 ** nn)))
s = time.perf_counter()
a = qtableread(n)
e = time.perf_counter()
print(a)
print(e - s)
