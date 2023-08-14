# coding: utf-8
import numpy as np
import chainer
import chainer.links as L
from chainer import optimizers, serializers
import chainer.functions as F

n_epoch = 50000  # エポック数(パラメータ更新回数)

# Prepare dataset
source = [[0, 0], [1, 0], [0, 1], [1, 1],[1,2],[1,3],[1,4],[1,5]]
target = [[0], [1], [1], [0],[2],[3],[4],[5]]
dataset = {}
dataset['source'] = np.array(source, dtype=np.float32)
dataset['target'] = np.array(target, dtype=np.float32)

# N = len(source)  # train data size

in_units = 2  # 入力層のユニット数
n_units = 8  # 隠れ層のユニット数
out_units = 1  # 出力層のユニット数

# モデルの定義
model = chainer.Sequential(L.Linear(in_units, n_units), F.sigmoid,
                           L.Linear(n_units, n_units), F.sigmoid,
                            L.Linear(n_units, n_units), F.sigmoid,
                           L.Linear(n_units, out_units))



# Setup optimizer
optimizer = optimizers.Adam()
optimizer.setup(model)

# Learning loop
loss_val = 100
epoch = 0
while loss_val > 1e-3:

    # training
    x = chainer.Variable(np.asarray(dataset['source']))  # source
    t = chainer.Variable(np.asarray(dataset['target']))  # target

    model.zerograds()  # 勾配をゼロ初期化
    y = model(x)  # 順伝搬

    loss = F.mean_squared_error(y, t)  # 平均二乗誤差

    loss.backward()  # 誤差逆伝播
    optimizer.update()  # 最適化

    # 途中結果を表示
    if epoch % 1000 == 0:
        # 誤差と正解率を計算
        loss_val = loss.data

        print('epoch:', epoch)
        print('x:\n', x.data)

        print('t:\n', t.data)

        print('y:\n', y.data)

        print('train mean loss={}'.format(loss_val))  # 訓練誤差, 正解率
        print(' - - - - - - - - - ')

    # n_epoch以上になると終了
    if epoch >= n_epoch:
        break

    epoch += 1
# modelとoptimizerを保存
# print('save the model')
# serializers.save_npz('xor_mlp.model', model)
# print('save the optimizer')
# serializers.save_npz('xor_mlp.state', optimizer)
