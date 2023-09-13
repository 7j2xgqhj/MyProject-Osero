import time
import numpy as np
import environment
from random import choice
from random import random
from numpy.random import choice as npchoice
from numpy import exp
import pickle
import os
import log

BLANK = 0  # 石が空：0
BLACK = 1  # 石が黒：1
WHITE = -1  # 石が白：2

SIZE = 8
GAMMA = 0.7  # 割引率
EPSILON = 0.9
TEMPERATURE = 0.01  # 温度定数初期値    上げると等確率　下げると強調　加算減算ではなく比で考えて調整するのがいいかも
EPTEMPERATURE = 1

WINREWORD = 1
LOSEREWORD = -1 * WINREWORD
DRAWREWORD = 0.01

PATH = os.path.abspath("..\\..\\qtables") + "/" + "table" + str(SIZE) + "/"

RAYER = int((SIZE * SIZE - 1) / 12)


def qtableread(filename: str, side: int):
    if side == 1:
        a = "b/"
    else:
        a = "w/"
    fn = "".join([filename[12 * i:12 * (i + 1)] + "/" for i in range(RAYER)])
    if os.path.isfile(PATH + a + fn + filename + ".pkl"):
        with open(PATH + a + fn + filename + ".pkl", 'rb') as f:
            data = pickle.load(f)
        return data
    else:
        return


def qtablesave(filename: str, obj: dict, side: int):
    if side == 1:
        a = "b/"
    else:
        a = "w/"
    fl = [filename[12 * i:12 * (i + 1)] + "/" for i in range(RAYER)]
    s = ""
    for l in fl:
        s += l
        if not os.path.isdir(PATH + a + s):
            os.mkdir(PATH + a + s)
    with open(PATH + a + s + filename + ".pkl", 'wb') as f:
        pickle.dump(obj, f)


def statetonum(state):
    statestr = ""
    for i in state:
        for j in i:
            statestr += str(j + 1)
    return statestr


class Agent:
    # 盤面の情報は、先手・後手(定数)、何手目(計算が簡単)、石値合計(np.sum(state))。打てる手数(ついでで使える)で分類して絞り込めるようにすることで計算時間を削減したい
    def __init__(self, side, mode=0):
        self.mode = mode
        self.side = side
        self.log = []
        self.gamma = GAMMA
        self.epsilon = EPSILON
        self.temperature = TEMPERATURE
        self.re = ""
        if side == BLACK:
            self.turn = 0
        elif side == WHITE:
            self.turn = 1

    def reset(self):
        self.epsilon, self.log, self.temperature = EPSILON, [], TEMPERATURE
        if self.side == BLACK:
            self.turn = 0
        elif self.side == WHITE:
            self.turn = 1

    def action(self, state, actlist):
        statesetlist = None
        stn = statetonum(state)
        if len(actlist) == 1:  # 選択肢が一つしかないとき
            act = actlist[0]
        elif self.mode == 1 and self.epsilon <= random():
            act = choice(actlist)
            statesetlist = qtableread(stn, self.side)
        else:
            statesetlist = qtableread(stn, self.side)
            if statesetlist is not None:
                if self.mode == 2:
                    act = self.softmaxchoice(dict=statesetlist)
                else:

                    act = self.maxreword(dict=statesetlist)
            else:
                act = choice(actlist)
        if self.mode == 1 and len(act) != 0 and len(actlist) > 1:
            self.log.append([self.turn, actlist, act, stn, statesetlist])
        self.turn += 2
        return act

    def maxreword(self, dict):
        m = list(dict.keys())[0]
        for k in dict.keys():
            if dict[k][1] > dict[m][1]:
                m = k
        return [int(m[1]), int(m[-2])]

    def softmaxchoice(self, dict):
        klist = list(dict.keys())
        vlist = [dict[k][1] for k in klist]
        q = [exp(a / self.temperature) for a in vlist]
        plist = [qa / sum(q) for qa in q]
        m = klist[npchoice(list(range(len(klist))), p=plist)]
        return [int(m[1]), int(m[-2])]

    def save(self, reword):  # dict[ターン数][石値合計][選択肢の数]=[[state,{行動:[試行回数,行動価値] ...}],...]
        # step[0]:ターン数、step[1]:選択肢の配列、step[2]:選択した行動、step[3]:盤面num step[4]:dict
        for t, step in enumerate(self.log):
            r = reword * self.gamma ** (len(self.log) - (t + 1))
            if step[4] is not None:
                q = step[4][str(step[2])]
                q += [1, (r - q[1]) / (q[0] + 1)]
                qtablesave(step[3], step[4], self.side)
            else:
                ql = {}
                for a in step[1]:
                    ql[str(a)] = np.array([0, 0], dtype=np.float32)
                ql[str(step[2])] += [1, r]
                qtablesave(step[3], ql, self.side)


def train(episode):
    agentw = Agent(side=WHITE, mode=1)
    agentb = Agent(side=BLACK, mode=1)
    env = environment.Environment(SIZE)
    for count in range(episode):
        env.reset()
        while env.getwinner().size == 0:
            state, actlist = env.getstate(), env.actlist
            if env.side == WHITE:
                env.action(agentw.action(state=state, actlist=actlist))
            else:
                env.action(agentb.action(state=state, actlist=actlist))
        winner = env.getwinner()
        if winner == WHITE:
            agentw.save(WINREWORD)
            agentb.save(LOSEREWORD)
        elif winner == BLACK:
            agentw.save(LOSEREWORD)
            agentb.save(WINREWORD)
        else:
            agentw.save(DRAWREWORD)
            agentb.save(DRAWREWORD)
        agentw.reset()
        agentb.reset()


def test(whiteside, blackside, set):
    wwin = 0
    bwin = 0
    draw = 0
    n = 0
    env = environment.Environment(SIZE)
    agentw = Agent(side=WHITE)
    agentb = Agent(side=BLACK)
    for count in range(set):
        env.reset()
        while env.getwinner().size == 0:
            state, actlist = env.getstate(), env.actlist
            if env.side == WHITE:
                if whiteside:
                    env.action(agentw.action(state=state, actlist=actlist))
                else:
                    env.action(choice(actlist))
            else:
                if blackside:
                    env.action(agentb.action(state=state, actlist=actlist))
                else:
                    env.action(choice(actlist))
        winner = env.getwinner()
        if winner == WHITE:
            wwin += 1
        elif winner == BLACK:
            bwin += 1
        else:
            draw += 1
        n += 1
        agentw.reset()
        agentb.reset()
    print("Wwin:" + str(wwin) + "回")
    print("Bwin:" + str(bwin) + "回")
    print("draw:" + str(draw) + "回")
    print("総試合数:" + str(n) + "回")
    return [wwin, bwin, draw, n]


def test2(whiteside, blackside, set):
    wwin = 0
    bwin = 0
    draw = 0
    n = 0
    env = environment.Environment(SIZE)
    agentw = Agent(side=WHITE, mode=2)
    agentb = Agent(side=BLACK, mode=2)
    for count in range(set):
        env.reset()
        while env.getwinner().size == 0:
            state, actlist = env.getstate(), env.actlist
            if env.side == WHITE:
                if whiteside:
                    env.action(agentw.action(state=state, actlist=actlist))
                else:
                    env.action(choice(actlist))
            else:
                if blackside:
                    env.action(agentb.action(state=state, actlist=actlist))
                else:
                    env.action(choice(actlist))
        winner = env.getwinner()
        if winner == WHITE:
            wwin += 1
        elif winner == BLACK:
            bwin += 1
        else:
            draw += 1
        n += 1
        agentw.reset()
        agentb.reset()
    print("Wwin:" + str(wwin) + "回")
    print("Bwin:" + str(bwin) + "回")
    print("draw:" + str(draw) + "回")
    print("総試合数:" + str(n) + "回")
    return [wwin, bwin, draw, n]


def t():
    logs = log.LOG(SIZE)
    testset = 1000
    trainset = 10000
    _, bwin, _, n = test(whiteside=False, blackside=True, set=testset)
    logs.save(bwin / n, 0)
    for i in range(10):
        s = time.perf_counter()
        print("train...")
        train(trainset)
        print("test...")
        _, bwin, _, n = test(whiteside=False, blackside=True, set=testset)
        e = time.perf_counter()
        print(e - s)
        logs.save(bwin / n, trainset)
    logs.show()


if __name__ == "__main__":
    if not os.path.isdir(PATH):
        os.mkdir(PATH)
    t()
    # test(whiteside=False, blackside=True, set=1000)
