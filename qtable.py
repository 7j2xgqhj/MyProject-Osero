import os
import pickle
from concurrent import futures


class Qtable:
    def __init__(self, size, save=False,mul=1):
        self.size = size
        self.path = "F:/qtables/table" + str(self.size) + "/"
        self.rayer = int((self.size ** 2 - 1) / 12)
        self.filelist = []
        self.cpath = os.path.abspath("..\\..\\qcash") + "/table" + str(self.size) + "/"
        self.save = save
        self.acs = mul*[""]
        self.num=0

    def qtableread(self, filename: str, side: int):
        num =self.num
        if self.num==0:
            self.num=1
        else:
            self.num=0
        while filename in self.acs:
            pass
        self.acs[num]=filename
        if side == 1:
            a = "b/"
        else:
            a = "w/"
        fn = "".join([filename[12 * i:12 * (i + 1)] + "/" for i in range(self.rayer)])
        if self.save:
            try:
                if os.path.isfile(self.cpath + a + fn + filename + ".pkl"):
                    with open(self.cpath + a + fn + filename + ".pkl", 'rb') as f:
                        data = pickle.load(f)
                    self.acs[num] = ""
                    return data
            except Exception as e:
                print(e)
                print("qt1:"+filename)
                print(self.acs)
        try:
            if os.path.isfile(self.path + a + fn + filename + ".pkl"):
                with open(self.path + a + fn + filename + ".pkl", 'rb') as f:
                    data = pickle.load(f)
                self.acs[num] = ""
                return data
            else:
                self.acs[num] = ""
                return
        except Exception as e:
            print(e)
            print("qt2:"+filename)
            self.acs[num] = ""

    def qtablesave(self, filename: str, obj: dict, side: int):
        while filename in self.acs:
            pass
        self.acs[self.acs.index("")]=filename
        if side == 1:
            a = "b/"
        else:
            a = "w/"
        fl = [filename[12 * i:12 * (i + 1)] + "/" for i in range(self.rayer)]
        s = ""
        for l in fl:
            s += l
            if not os.path.isdir(self.cpath + a + s):
                os.mkdir(self.cpath + a + s)
        with open(self.cpath + a + s + filename + ".pkl", 'wb') as f:
            pickle.dump(obj, f)
            if not [filename, a] in self.filelist:
                self.filelist.append([filename, a])
        self.acs[self.acs.index(filename)] = ""

    def fs(self, fn):
        fl = [fn[0][12 * i:12 * (i + 1)] + "/" for i in range(self.rayer)]
        if os.path.isfile(self.cpath + fn[1] + "".join(fl) + fn[0] + ".pkl"):
            with open(self.cpath + fn[1] + "".join(fl) + fn[0] + ".pkl", 'rb') as f:
                data = pickle.load(f)
            os.remove(self.cpath + fn[1] + "".join(fl) + fn[0] + ".pkl")
            s = ""
            for l in fl:
                s += l
                if not os.path.isdir(self.path + fn[1] + s):
                    os.mkdir(self.path + fn[1] + s)
            with open(self.path + fn[1] + s + fn[0] + ".pkl", 'wb') as f:
                pickle.dump(data, f)

    def finalsave(self):
        with futures.ThreadPoolExecutor(max_workers=4) as executor:
            for fn in self.filelist:
                executor.submit(self.fs, fn)
