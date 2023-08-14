import numpy as np
import environment
from random import choice
from random import random
from numpy.random import choice as npchoice
import matplotlib.pyplot as plt
from numpy import exp
from chainer import serializers
import os
import net
import math
import time

BLANK = 0  # 石が空：0
BLACK = 1  # 石が黒：1
WHITE = -1  # 石が白：2

SIZE = 4
GAMMA = 0.7  # 割引率
EPSILON = 0.9
TEMPERATURE = 1  # 温度定数初期値    上げると等確率　下げると強調　加算減算ではなく比で考えて調整するのがいいかも
EPTEMPERATURE = 1

WINREWORD = 1
LOSEREWORD = -1 * WINREWORD
DRAWREWORD = 0.5

LOGLIMIT=10
#mode0 maxchoice mode1 epsilon and learn on mode2 softmax
class Agent:
    def __init__(self, side, mode=0):
        self.mode = mode
        self.side = side
        self.log = []
        self.epsilon = EPSILON
        self.temperature = TEMPERATURE
        if side == BLACK:
            if os.path.isfile('balck.npz'):
                self.tables=net.Net('balck.npz')
            else:
                self.tables = net.Net()
            self.turn = 0
        elif side == WHITE:
            if os.path.isfile('white.npz'):
                self.tables=net.Net('white.npz')
            else:
                self.tables = net.Net()
            self.turn = 1

    def reset(self):
        self.epsilon, self.log, self.temperature = EPSILON, [], TEMPERATURE
        if self.side == BLACK:
            self.turn = 0
        elif self.side == WHITE:
            self.turn = 1
    def stateTonum(self,state):
        strstate=""
        for y in state:
            for x in y:
              strstate+=str(int(x+1))
        return int(strstate)

    def action(self, state, actlist):  ##testとtrainをまとめたい　方策と記録のとこだけ変える
        if len(actlist) == 1:  # 選択肢が一つしかないとき
            act = actlist[0]
        elif self.mode == 1 and self.epsilon <= random():
            act = choice(actlist)
        else:
            if self.mode == 2:
                act = self.softmaxchoice(state=state,actlist=actlist)
            else:
                act = self.maxreword(state=state,actlist=actlist)
        if self.mode == 1 and len(actlist) > 1:
            self.log.append([self.stateTonum(state),act[0],act[1]])
        self.turn += 2
        return act
    def maxreword(self, state,actlist):
        set = [[a, self.tables.getQ([self.stateTonum(state),a[0],a[1]])] for a in actlist]
        act = choice([i[0] for i in set if i[1] == max([i[1] for i in set])])
        return act

    def softmaxchoice(self, state,actlist):
        vlist = [self.tables.getQ([self.stateTonum(state),a[0],a[1]]) for a in actlist]
        q = [exp(a / self.temperature) for a in vlist]
        plist = [qa / sum(q) for qa in q]
        act = actlist[npchoice(list(range(len(actlist))), p=plist)]
        return act

    def save(self, reword):
        self.tables.train(self.log,reword)

    def savedict(self):
        self.tables.save(self.side)

def train(episode):
    lognpz = np.load('log.npz')
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
        if count % (episode/10)==0:
            print(str(count / (episode/100))+"%")
    agentb.savedict()
    agentw.savedict()
    logcount=lognpz['count']
    logcount[0]+=episode
    np.savez('log.npz', x=lognpz['x'], y=lognpz['y'], ave=lognpz['ave'],count=logcount)

def test(whiteside, blackside, set):
    lognpz = np.load('log.npz')
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
            actlist = env.actlist
            if env.side == WHITE:
                if whiteside:
                    env.action(agentw.action(state=env.getstate(), actlist=actlist))
                else:
                    env.action(choice(actlist))
            else:
                if blackside:
                    env.action(agentb.action(state=env.getstate(), actlist=actlist))
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
    logx = lognpz['x']
    logy = lognpz['y']
    logave = lognpz['ave']
    logy = np.append(logy, bwin / n)
    logx = np.append(logx, lognpz['count'])
    logave = np.append(logave, np.mean(logy))
    np.savez('log.npz', x=logx, y=logy, ave=logave,count=lognpz['count'])
    return [wwin, bwin, draw, n]


def test2(whiteside, blackside, set):
    dictw = np.load('tablewhite.npy', allow_pickle=True).item()
    dictb = np.load('tableblack.npy', allow_pickle=True).item()
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
            actlist = env.actlist
            if env.side == WHITE:
                if whiteside:
                    env.action(agentw.action(state=env.getstate(), actlist=actlist))
                else:
                    env.action(choice(actlist))
            else:
                if blackside:
                    env.action(agentb.action(state=env.getstate(), actlist=actlist))
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


def resetW():
    np.save('tablewhite.npy', np.array({'count': 0}))


def resetB():
    np.save('tableblack.npy', np.array({'count': 0}))


def resetlog():
    np.savez('log.npz', x=np.array([]), y=np.array([]), ave=np.array([]),count=np.array([0]))


def dictcheckW():
    dictw = np.load('tablewhite.npy', allow_pickle=True).item()
    print(dictw)


def param():
    colors = ["blue", "red", "green", "yellow", "black"]
    fig, ax = plt.subplots()
    ax.set_xlabel('train')  # x軸ラベル
    ax.set_ylabel('win')  # y軸ラベル
    ax.grid()
    nums = [0.9, 0.8, 0.7, 0.6, 0.5]

    def tr():
        resetB()
        resetW()
        testset = 1000
        num = 0
        x = [0]
        c = 100
        ave = np.array([test(whiteside=False, blackside=True, set=testset)[1], testset])
        y = [ave[0] / ave[1]]
        for i in range(40):
            train(c)
            num += c
            x.append(num)
            ave += test(whiteside=False, blackside=True, set=testset)[1], testset
            y.append(ave[0] / ave[1])
        return x, y

    for n, c in zip(nums, colors):
        EPSILON = n
        x, y = tr()
        ax.plot(x, y, color=c, label=str(EPSILON))
    plt.legend()
    plt.show()


def t():
    testset = 1000
    test(whiteside=False, blackside=True, set=testset)
    for i in range(10):
        train(1000)
        test(whiteside=False, blackside=True, set=testset)
    lognpz = np.load('log.npz')
    logx = lognpz['x']
    logy = lognpz['ave']
    print(logx)
    print(logy)
    plt.plot(logx, logy)
    plt.show()


if __name__ == "__main__":
    resetlog()
    t()
