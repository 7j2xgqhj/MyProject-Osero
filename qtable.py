import os
import pickle
import shutil
from parameter import Parameter
import numpy as np


SIZE = Parameter.SIZE
PATH = Parameter.PATH
CPATH = Parameter.CPATH
patternmatch = Parameter.patternmatch


def statetonum(state):
    statestr = ""
    for i in state:
        for j in i:
            statestr += str(j + 1)
    return statestr


class Qtable:
    def __init__(self):
        self.size = SIZE
        self.path = PATH
        self.rayer = int((self.size ** 2 - 1) / 12)
        self.filelist = []
        self.cpath = CPATH
        self.tpath=CPATH+"tdict/"
        self.patternweight = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    def qtableread(self, state, side: int):
        st = np.where(state > 2, 2, state)
        if side == 1:
            a = "b/"
        else:
            a = "w/"
        for i in range(2):
            for j in range(4):
                if i == 0:
                    x = np.copy(st)
                    stl = np.copy(state)
                else:
                    x = np.fliplr(st)
                    stl = np.fliplr(state)
                x = np.rot90(x, j)
                stl = np.rot90(stl, j)
                stn = statetonum(x)
                fn = "".join([stn[12 * i:12 * (i + 1)] + "/" for i in range(self.rayer)])
                data = None
                if os.path.isfile(self.cpath + a + fn + stn + ".pkl"):
                    with open(self.cpath + a + fn + stn + ".pkl", 'rb') as f:
                        data = pickle.load(f)
                elif os.path.isfile(self.path + a + fn + stn + ".pkl"):
                    with open(self.path + a + fn + stn + ".pkl", 'rb') as f:
                        data = pickle.load(f)
                if data is not None:
                    di = {}
                    li = {}
                    for i in list(zip(*np.where(stl > 1))):
                        ac = [i[0], i[1]]
                        n = stl[i[0]][i[1]]
                        nl = list(zip(*np.where(state == n)))[0]
                        di[str([nl[0], nl[1]])] = data[str(ac)]
                        li[str([nl[0], nl[1]])] = str(ac)
                    return di, [stn, li]
        return None, [statetonum(st), None]

    def qtablesave(self, lt, obj: dict, side: int):
        stn, li = lt[0], lt[1]
        if side == 1:
            a = "b/"
        else:
            a = "w/"
        fn = "".join([stn[12 * i:12 * (i + 1)] + "/" for i in range(self.rayer)])
        if os.path.isfile(self.cpath + a + fn + stn + ".pkl"):
            di = {}
            for k in obj.keys():
                di[li[k]] = obj[k]
            with open(self.cpath + a + fn + stn + ".pkl", 'wb') as f:
                pickle.dump(di, f)
            # if not [self.cpath + a + fn + stn + ".pkl", a] in self.filelist:
            #    self.filelist.append([stn, a])
            return
        fl = [stn[12 * i:12 * (i + 1)] + "/" for i in range(self.rayer)]
        s = ""
        for l in fl:
            s += l
            if not os.path.isdir(self.cpath + a + s):
                os.mkdir(self.cpath + a + s)
        with open(self.cpath + a + s + stn + ".pkl", 'wb') as f:
            pickle.dump(obj, f)
        #    if not [stn, a] in self.filelist:
        #        self.filelist.append([stn, a])

    def finalsave(self):  # ここ事故
        for fn in self.filelist:
            fl = [fn[0][12 * i:12 * (i + 1)] + "/" for i in range(self.rayer)]
            if os.path.isfile(self.cpath + fn[1] + "".join(fl) + fn[0] + ".pkl"):
                s = ""
                for l in fl:
                    s += l
                    if not os.path.isdir(self.path + fn[1] + s):
                        os.mkdir(self.path + fn[1] + s)
                shutil.move(self.cpath + fn[1] + "".join(fl) + fn[0] + ".pkl",
                            self.path + fn[1] + "".join(fl) + fn[0] + ".pkl")

    def setsave(self, state, r, side):
        stn = statetonum(state)
        fn="".join([stn[12 * i:12 * (i + 1)] + "/" for i in range(self.rayer)])
        if os.path.isfile(self.tpath + fn + stn + ".pkl"):
            with open(self.tpath + fn + stn + ".pkl","rb") as f:
                data = pickle.load(f)
            data[str(side)]+=[1, (r - data[str(side)][1]) / (data[str(side)][0] + 1)]
            with open(self.tpath + fn + stn + ".pkl", "wb") as f:
                pickle.dump(data, f)
        else:
            fl = [stn[12 * i:12 * (i + 1)] + "/" for i in range(self.rayer)]
            s = ""
            for l in fl:
                s += l
                if not os.path.isdir(self.tpath + s):
                    os.mkdir(self.tpath + s)
            data={"1":np.array([0, 0], dtype=np.float32),"-1":np.array([0, 0], dtype=np.float32)}
            data[str(side)] += [1, (r - data[str(side)][1]) / (data[str(side)][0] + 1)]
            with open(self.tpath + s + stn + ".pkl", 'wb') as f:
                pickle.dump(data, f)

    def tablesave(self, state, r, side):
        st = np.where(state >= 2, 0, state)
        for p in patternmatch:
            for i in range(4):
                instate = st * np.rot90(p, i)
                self.setsave(np.rot90(instate, -i), r, side)

    def getstatevalue(self, state, side):
        st = np.where(state >= 2, 0, state)
        sm = 0
        for p,pw in zip(patternmatch,self.patternweight):
            for i in range(4):
                x=1
                if np.array_equal(p,np.rot90(p, i)):
                    x=0.5
                instate = st * np.rot90(p, i)
                stn = statetonum(np.rot90(instate, -i))
                fn = "".join([stn[12 * i:12 * (i + 1)] + "/" for i in range(self.rayer)])
                if os.path.isfile(self.tpath + fn + stn + ".pkl"):
                    with open(self.tpath + fn + stn + ".pkl", "rb") as f:
                        data = pickle.load(f)
                    n=data[str(side)][1]
                else:
                    n=0
                n*=x
                n+=pw
                sm += n
        return sm
    def settest(self,pw):
        self.patternweight=pw
