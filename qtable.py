import os
import pickle



class Qtable:
    def __init__(self, size, save=False,path=None):
        self.size = size
        self.path = path
        self.rayer = int((self.size ** 2 - 1) / 12)
        self.filelist = []
        self.cpath = os.path.abspath("..\\..\\qcash") + "/table" + str(self.size) + "/"
        self.save = save

    def qtableread(self, filename: str, side: int):
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
                    return data
            except Exception as e:
                print(e)
                print("qt1:"+filename)
        try:
            if os.path.isfile(self.path + a + fn + filename + ".pkl"):
                with open(self.path + a + fn + filename + ".pkl", 'rb') as f:
                    data = pickle.load(f)
                return data
            else:
                return
        except Exception as e:
            print(e)
            print("qt2:"+filename)


    def qtablesave(self, filename: str, obj: dict, side: int):
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



    def finalsave(self):
        for fn in self.filelist:
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

