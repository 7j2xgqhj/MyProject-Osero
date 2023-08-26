import numpy as np


class Qtable:
    def __init__(self, reset=False):
        if reset:
            np.save('tablewhite.npy', np.array({'count': 0}))
            np.save('tableblack.npy', np.array({'count': 0}))
        self.white = np.load('tablewhite.npy', allow_pickle=True).item()
        self.black = np.load('tableblack.npy', allow_pickle=True).item()

    def save(self):
        np.save('tableblack.npy', self.white)
        np.save('tablewhite.npy', self.black)
