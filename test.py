import pickle
import time
import os
import numpy as np
import matplotlib.pyplot as plt
import os

BLANK = 0  # 石が空：0
BLACK = 1  # 石が黒：1
WHITE = -1  # 石が白：2
SIZE = 6
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
        else:
            return
    except:
        print(filename)


st = "201111101111102211102211111211111111"
di = qtableread(st, BLACK)
klist = list(di.keys())
vlist = [di[k][1] for k in klist]
print(vlist)
x = []
y=[[] for i in range(len(vlist))]
for temperature in range(1,300):
    tmp=temperature*0.001
    q = [np.exp(a / tmp) for a in vlist]
    plist = [qa / sum(q) * 100 for qa in q]
    x.append(tmp)
    for yl ,pl in zip(y,plist):
        yl.append(pl)
for yl in y:
    plt.plot(x, yl)
plt.show()
