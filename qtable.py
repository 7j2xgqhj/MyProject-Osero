import os
import pickle
import shutil

import numpy as np


def statetonum(state):
    statestr = ""
    for i in state:
        for j in i:
            statestr += str(j + 1)
    return statestr


class Qtable:
    def __init__(self, size, save=False, path=None):
        self.size = size
        self.path = path
        self.rayer = int((self.size ** 2 - 1) / 12)
        self.filelist = []
        self.cpath = os.path.abspath("..\\..\\qcash") + "/table" + str(self.size) + "/"
        self.save = save

    def qtableread(self, state, side: int):
        st = np.where(state > 2, 2,state)
        if side == 1:
            a = "b/"
        else:
            a = "w/"
        for i in range(2):
            for j in range(4):
                if i ==0:
                    x = np.copy(st)
                    stl = np.copy(state)
                else:
                    x = np.fliplr(st)
                    stl = np.fliplr(state)
                x=np.rot90(x, j)
                stl=np.rot90(stl,j)
                stn=statetonum(x)
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
                    li={}
                    for i in list(zip(*np.where(stl > 1))):
                        ac = [i[0], i[1]]
                        n = stl[i[0]][i[1]]
                        nl = list(zip(*np.where(state == n)))[0]
                        if not str(ac) in data.keys():
                            print(data)
                            print(data.keys())
                            print(ac)
                            print(list(zip(*np.where(stl > 1))))
                            print(a + fn + stn + ".pkl")
                            print(os.path.isfile(self.cpath + a + fn + stn + ".pkl"))
                            print(os.path.isfile(self.path + a + fn + stn + ".pkl"))
                            print(state)
                            print(x)
                            print(stl)
                        di[str([nl[0], nl[1]])] = data[str(ac)]
                        li[str([nl[0], nl[1]])]=str(ac)
                    return di,[stn,li]
        return None,[statetonum(st),None]

    def qtablesave(self, lt, obj: dict, side: int):
        stn,li=lt[0],lt[1]
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
            if not [self.cpath + a + fn + stn + ".pkl", a] in self.filelist:
                self.filelist.append([stn, a])
            return
        fl = [stn[12 * i:12 * (i + 1)] + "/" for i in range(self.rayer)]
        s = ""
        for l in fl:
            s += l
            if not os.path.isdir(self.cpath + a + s):
                os.mkdir(self.cpath + a + s)
        with open(self.cpath + a + s + stn + ".pkl", 'wb') as f:
            pickle.dump(obj, f)
            if not [stn, a] in self.filelist:
                self.filelist.append([stn, a])

    def finalsave(self):#ここ事故
        for fn in self.filelist:
            fl = [fn[0][12 * i:12 * (i + 1)] + "/" for i in range(self.rayer)]
            if os.path.isfile(self.cpath + fn[1] + "".join(fl) + fn[0] + ".pkl"):
                s = ""
                for l in fl:
                    s += l
                    if not os.path.isdir(self.path + fn[1] + s):
                        os.mkdir(self.path + fn[1] + s)
                shutil.move(self.cpath + fn[1] + "".join(fl) + fn[0] + ".pkl",self.path + fn[1] + "".join(fl) + fn[0] + ".pkl")
