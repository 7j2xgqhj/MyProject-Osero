import numpy as np
import chainer
import chainer.links as L
from chainer import optimizers, serializers
import chainer.functions as F
from chainer import Variable

BLANK = 0  # 石が空：0
BLACK = 1  # 石が黒：1
WHITE = -1  # 石が白：2

in_units = 3  # 入力層のユニット数
n_units = 10  # 隠れ層のユニット数
out_units = 1  # 出力層のユニット数
class Net:
    # 初期化
    def __init__(self,path=None):
        self.model = chainer.Sequential(L.Linear(in_units, n_units), F.sigmoid,
                                        L.Linear(n_units, n_units), F.sigmoid,
                                        L.Linear(n_units, n_units), F.sigmoid,
                                        L.Linear(n_units, n_units), F.sigmoid,
                                        L.Linear(n_units, n_units), F.sigmoid,
                                        L.Linear(n_units, n_units), F.sigmoid,
                                        L.Linear(n_units, n_units), F.sigmoid,
                                         L.Linear(n_units, out_units))
        if path !=None:
            serializers.load_npz(path, self.model)
        self.optimizer = optimizers.Adam()
        self.optimizer.setup(self.model)
        self.n_epoch = 500000
    def getQ(self,sorce):
        return self.model(chainer.Variable(np.array([sorce], dtype=np.float32))).data[0][0]
    def train(self,log,r):#log =[[盤面番号,行動のx,行動のy],...]
        source= np.array(log, dtype=np.float32)
        target = np.array([[(self.getQ(i)+r)/2] for i in log], dtype=np.float32)
        loss_val = 100
        epoch = 0
        while loss_val > 1e-3:
            self.model.zerograds()  # 勾配をゼロ初期化
            loss = F.mean_squared_error(self.model(Variable(np.asarray(source))), Variable(np.asarray(target)))  # 平均二乗誤差
            loss.backward()  # 誤差逆伝播
            self.optimizer.update()  # 最適化
            if epoch % 1000 == 0:
                loss_val = loss.data
            if epoch >= self.n_epoch:
                break
            epoch += 1
    def save(self,side):
        if side ==BLACK:
            serializers.save_npz("black.npz", self.model)
        elif side ==WHITE:
            serializers.save_npz("white.npz", self.model)


