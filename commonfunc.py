import numpy as np
from numpy import copy
from parameter import Parameter
from numpy import exp

SIZE = Parameter.SIZE
BLANK = Parameter.BLANK
BLACK = Parameter.BLACK
WHITE = Parameter.WHITE


def reversestones(side, index, instate):  # 引数に座標、出力は変化後の盤面orダメだったらfalse
    side = side * -1
    arrayclone = copy(instate)  # 参照渡し対策　必須
    for i in [[0, -1], [1, -1], [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1]]:
        localindex, directon, returnstonelist, isdifferentcoloredstone = np.array(index,
                                                                                  dtype=np.int8), i, [], False
        localindex = np.add(localindex, directon)  # 各方向にひとつづつ進める
        while np.all(localindex >= 0) and np.all(localindex < SIZE):
            if arrayclone[localindex[0]][localindex[1]] != BLACK and arrayclone[localindex[0]][
                localindex[1]] != WHITE:
                break
            elif arrayclone[localindex[0]][localindex[1]] == -1 * side:  # 異なる色の石がある
                isdifferentcoloredstone = True
                returnstonelist.append(copy(localindex))
            elif isdifferentcoloredstone:  # ↑の状態を経た後かつ同じ色の石がある ひっくり返せる
                for num in returnstonelist:
                    arrayclone[num[0]][num[1]] = side
                break
            else:  # 上以外(同じ色しかない)
                break
            localindex = np.add(localindex, directon)  # 各方向にひとつづつ進める

    difference = abs(np.sum(np.copy(instate) - arrayclone))
    arrayclone[index[0]][index[1]] = side
    return arrayclone, difference


def makeactivemass(state, side):
    ind = []
    st = copy(state)
    for i in range(SIZE):
        for j in range(SIZE):
            if st[i][j] == BLANK:
                s, dif = reversestones(side, [i, j], st)
                if dif != 0:
                    ind.append([i, j])
    for i in ind:
        st[i[0]][i[1]] = 2
    return st


def probabilityfunc(vlist, tmp):
    b = [a / tmp for a in vlist]
    q = [exp(i) for i in b]
    if float('inf') in q:
        n = 1
        while float('inf') in q:
            n *= 10
            b = [a / n for a in b]
            q = [exp(i) for i in b]
    while 0 in q:
        q[q.index(0)] += 0.001
    q = [i / max(q) for i in q]
    return np.array([qa / sum(q) for qa in q])
