import pickle
import time
import os
import numpy as np
import matplotlib.pyplot as plt
import os
import environment

BLANK = 0  # 石が空：0
BLACK = 1  # 石が黒：1
WHITE = -1  # 石が白：2
SIZE = 8
# PATH = os.path.abspath("..\\..\\qtables") + "/" + "table" + str(SIZE) + "/"
PATH = "E:/qtables/" + "table" + str(SIZE) + "/"
RAYER = int((SIZE * SIZE - 1) / 12)


def qtableread(filename: str, side: int):
    if side == 1:
        a = "b/"
    else:
        a = "w/"
    fn = "".join([filename[12 * i:12 * (i + 1)] + "/" for i in range(RAYER)])
    try:
        if os.path.isfile(PATH + a + fn + filename + ".pkl"):
            with open(PATH + a + fn + filename + ".pkl", 'rb') as f:
                data = pickle.load(f)
            return data
    except:
        print(filename)


env = environment.Environment(SIZE)
a = env.state
print(a)
b = np.rot90(a,1)
print(b)
c=np.flipud(a)
#print(c)
d=np.where(c>1,0,c)
print(d)
e=list(zip(*np.where(a==2)))[0]
print(e)
print([[i[0],i[1]]for i in list(zip(*np.where(a > 1)))])
print(str([1,2])[-2])