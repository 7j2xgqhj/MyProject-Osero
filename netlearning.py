# coding: utf-8
import numpy as np
import chainer
import chainer.links as L
from chainer import optimizers, serializers
import chainer.functions as F
import os
from parameter import Parameter
n_epoch = 50000  # エポック数(パラメータ更新回数) 一つの訓練データを何回繰り返して学習させるか
in_units = Parameter.SIZE**2  # 入力層のユニット数
n_units = 20  # 隠れ層のユニット数
out_units = 1  # 出力層のユニット数
filename='my_iris'+str(in_units)+'.net'
def modelset():
    model = chainer.Sequential(L.Linear(in_units, n_units), F.sigmoid,
                               L.Linear(n_units, n_units), F.sigmoid,
                               L.Linear(n_units, n_units), F.sigmoid,
                               L.Linear(n_units, n_units), F.sigmoid,
                               L.Linear(n_units, n_units), F.sigmoid,
                               L.Linear(n_units, out_units))
    if os.path.isfile(filename):
        chainer.serializers.load_npz(filename, model)
    return model
def netlearning(sources,targets):
    # N = len(source)  # train data size
    model = modelset()
    # Prepare dataset
    #source = [[0, 0], [1, 0], [0, 1], [1, 1], [1, 2], [1, 3], [1, 4], [1, 5]]
    #target = [[0], [1], [1], [0], [2], [3], [4], [5]]
    print(len(sources[0]))
    source=sources
    target=targets
    dataset = {'source': np.array(source, dtype=np.float32), 'target': np.array(target, dtype=np.float32)}
    # Setup optimizer
    optimizer = optimizers.Adam()
    optimizer.setup(model)
    # Learning loop
    loss_val = 100
    epoch = 0
    while loss_val > 1e-4:

        # training
        x = chainer.Variable(np.asarray(dataset['source']))  # source
        t = chainer.Variable(np.asarray(dataset['target']))  # target

        # 勾配をゼロ初期化
        model.zerograds()
        y = model(x)  # 順伝搬

        loss = F.mean_squared_error(y, t)  # 平均二乗誤差

        loss.backward()  # 誤差逆伝播
        optimizer.update()  # 最適化

        # 途中結果を表示
        if epoch % 1000 == 0:
            # 誤差と正解率を計算
            loss_val = loss.data

            #print('epoch:', epoch)
            #print('x:\n', x.data)

            #print('t:\n', t.data)

            #print('y:\n', y.data)

            #print('train mean loss={}'.format(loss_val))  # 訓練誤差, 正解率
            #print(' - - - - - - - - - ')

        # n_epoch以上になると終了
        if epoch >= n_epoch:
            break

        epoch += 1
    chainer.serializers.save_npz(filename, model)

def getval(state):
    model = modelset()
    #print(state)
    y=model(np.asarray(np.array([state], dtype=np.float32)))
    return y.data