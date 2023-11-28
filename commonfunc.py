import random

import numpy as np
from numpy import copy
from parameter import Parameter
from numpy import exp

SIZE = Parameter.SIZE
BLANK = Parameter.BLANK
BLACK = Parameter.BLACK
WHITE = Parameter.WHITE
priority_action = Parameter.priority_action
not_priority_action = Parameter.not_priority_action


def reversestones(side, index, instate):  # 引数に座標、出力は変化後の盤面orダメだったらfalse
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
            if st[i][j] == BLANK or st[i][j] > 1:
                s, dif = reversestones(side, [i, j], st)
                if dif != 0:
                    ind.append([i, j])
    for i in ind:
        st[i[0]][i[1]] = 2
    return st


def staterating(state, side):
    st = copy(state)
    s = makeactivemass(st, side)
    return -1 * np.count_nonzero(s == 2)


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


def foreseeingfunc(side, instate, actlist):
    score = []
    for act in actlist:
        st, _ = reversestones(index=act, side=side, instate=instate)
        score.append(-1*staterating(st, side * -1))
    return score


def foreseeingfunc_ver1(actlist):
    for a in priority_action:
        if a in actlist:
            return a
    l = copy(actlist).tolist()
    al = list(filter(lambda x: x not in not_priority_action, l))
    if len(al) > 0:
        return random.choice(al)
    else:
        return random.choice(actlist)


def foreseeingfunc_ver2(side, instate, actlist):
    for a in priority_action:
        if a in actlist:
            return a
    l = copy(actlist).tolist()
    al = list(filter(lambda x: x not in not_priority_action, l))
    if len(al) > 0:
        score = []
        for act in actlist:
            st, _ = reversestones(index=act, side=side, instate=instate)
            s = makeactivemass(state=st, side=side * -1)
            point = 0
            for i in not_priority_action:
                if s[i[0]][i[1]] == 2:
                    point += 1
            for i in priority_action:
                if s[i[0]][i[1]] == 2:
                    point -= 12
            score.append(point)
        if np.all(np.array(score) == score[0]):
            return foreseeingfunc_ver3(side, instate, actlist)
        else:
            return actlist[score.index(max(score))]
    else:
        return random.choice(actlist)


def foreseeingfunc_ver3(side, instate, actlist):
    p = foreseeingfunc(side, instate, actlist)
    return actlist[p.index(max(p))]


def foreseeingfunc_ver4(side, instate, actlist,qtb):
    score = []
    stlist = []
    for act in actlist:
        st, _ = reversestones(index=act, side=side, instate=instate)
        score.append(-1 * qtb.getstatevalue(st, side * -1))
        stlist.append(st)
    mi=score.index(min(score))
    for ind,act in enumerate(actlist):
        if mi != ind:
            st, _ = reversestones(index=act, side=side, instate=instate)
            s = makeactivemass(state=st, side=side * -1)
            c = np.count_nonzero(s == 2)
            al = []
            for i in range(c):
                id = np.where(s == 2)
                al.append([id[0][i], id[1][i]])
            sc=[]
            for a in al:
                sst, _ = reversestones(index=a, side=side*-1, instate=st)
                sc.append(qtb.getstatevalue(sst, side))
            score[ind]+=sum(sc)
    return score


def absearch(side, state, n=0):
    n += 1
    st = makeactivemass(state, side)
    c = np.count_nonzero(st == 2)
    actlist = []
    for i in range(c):
        id = np.where(st == 2)
        actlist.append([id[0][i], id[1][i]])
    if len(actlist) >1:
        statelist = []
        score = []
        for a in actlist:
            s, _ = reversestones(side, a, state)
            statelist.append(s)
            score.append(staterating(s, side * -1))
    else:
        s, _ = reversestones(side, actlist[0], state)
        absearch(side*-1,s,n)

print(probabilityfunc([3,4,1],1))