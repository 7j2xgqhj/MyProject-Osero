import numpy as np
import chainer
import chainer.links as L
import chainer.functions as F
from chainer import optimizers
n_epoch=10000
source = [[0, 0], [1, 0], [0, 1], [1, 1]]
target = [[0], [1], [1], [0]]
dataset = {}
dataset['source'] = np.array(source, dtype=np.float32)
dataset['target'] = np.array(target, dtype=np.float32)
N = len(source) # train data size

in_units  = 2   # 入力層のユニット数
n_units   = 5   # 隠れ層のユニット数
out_units = 1   # 出力層のユニット数

#モデルの定義
model = chainer.Chain(l1=L.Linear(in_units, n_units),
                      l2=L.Linear(n_units , out_units))
def forward(x, t):
    h1 = F.sigmoid(model.l1(x))
    return model.l2(h1)

# Setup optimizer
optimizer = optimizers.Adam()
optimizer.setup(model)

# Learning loop
loss_val = 100
epoch = 0
while loss_val > 1e-5:

    # training
    x = chainer.Variable(np.asarray(dataset['source'])) #source
    t = chainer.Variable(np.asarray(dataset['target'])) #target

    model.zerograds()       # 勾配をゼロ初期化
    y    = forward(x, t)    # 順伝搬

    loss = F.mean_squared_error(y, t) #平均二乗誤差

    loss.backward()              # 誤差逆伝播
    optimizer.update()           # 最適化

    # 途中結果を表示
    if epoch % 1000 == 0:
        #誤差と正解率を計算
        loss_val = loss.data

        print('epoch:', epoch)
        print('x:\n', x.data)
        print('t:\n', t.data)
        print('y:\n', y.data)

        print('train mean loss={}'.format(loss_val)) # 訓練誤差, 正解率
        print(' - - - - - - - - - ')

    # n_epoch以上になると終了
    if epoch >= n_epoch:
        break

    epoch += 1