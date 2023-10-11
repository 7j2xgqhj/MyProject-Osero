import pickle
import os
import matplotlib.pyplot as plt

class LOG:
    def __init__(self,num):
        self.num=num
        self.f=False
        if os.path.isfile("log"+str(num)+".pkl"):
            with open("log"+str(num)+".pkl", 'rb') as f:
                self.data = pickle.load(f)
        else:
            self.data = {"x":[],"y":[],"max":0}
    def save(self,y,count):
        while self.f:
            pass
        self.f=True
        self.data["y"].append(y)
        self.data["max"]+=count
        self.data["x"].append(self.data["max"])
        self.f=False
    def end(self):
        with open("log"+str(self.num)+".pkl", 'wb') as f:
            pickle.dump(self.data, f)
    def show(self):
        plt.plot(self.data["x"], self.data["y"])
        plt.show()
