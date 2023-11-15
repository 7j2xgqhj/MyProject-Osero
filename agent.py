import threading
import time
import numpy as np
import environment
from random import choice
from random import random
from numpy.random import choice as npchoice
import pickle
import os
import log
import tkinter as tk
import envgui
import matplotlib.pyplot as plt
import qtable
from numpy import copy
from agent2 import Agent2
from parameter import Parameter
import commonfunc as cf

BLANK = Parameter.BLANK
BLACK = Parameter.BLACK
WHITE = Parameter.WHITE

SIZE = Parameter.SIZE
GAMMA = Parameter.GAMMA
EPSILON = Parameter.EPSILON
TEMPERATURE = Parameter.TEMPERATURE

WINREWORD = Parameter.WINREWORD
LOSEREWORD = Parameter.LOSEREWORD
DRAWREWORD = Parameter.DRAWREWORD

PATH = Parameter.PATH
RAYER = Parameter.RAYER
VALUERATE = Parameter.VALUERATE


def maxreword(dict):
    m = list(dict.keys())[0]
    for k in dict.keys():
        if dict[k][1] > dict[m][1]:
            m = k
    return [int(m[1]), int(m[-2])]


def graph(di, le):
    klist = list(di.keys())
    vlist = sorted([di[k][1] for k in klist])
    x = []
    y = []
    for temperature in range(1, 500):
        tmp = temperature * 0.001
        q = [np.exp(a / tmp) for a in vlist]
        plist = [qa / sum(q) * 100 for qa in q]
        x.append(tmp)
        y.append(plist[-2] / (1 / le))
    plt.plot(x, y)


class Agent:
    # 盤面の情報は、先手・後手(定数)、何手目(計算が簡単)、石値合計(np.sum(state))。打てる手数(ついでで使える)で分類して絞り込めるようにすることで計算時間を削減したい
    def __init__(self, side, mode=0, env=None, tmp=TEMPERATURE, tmpupdate=False, qtable=qtable.Qtable()):
        self.mode = mode
        self.side = side
        self.log = []
        self.gamma = GAMMA
        self.epsilon = EPSILON
        self.temperature = tmp
        self.deftmp = tmp
        self.environment = env
        self.prevalue = 0
        self.count = 0
        self.istmpupdate = tmpupdate
        self.qtable = qtable
        self.priority_action = Parameter.priority_action
        self.not_priority_action = Parameter.not_priority_action
        if side == BLACK:
            self.turn = 0
        elif side == WHITE:
            self.turn = 1

    def reset(self):
        self.epsilon, self.log, self.temperature = EPSILON, [], self.deftmp
        if self.side == BLACK:
            self.turn = 0
        elif self.side == WHITE:
            self.turn = 1

    def action(self):
        statesetlist = None
        qr = ""
        self.epsilon -= 0.02
        if self.mode == 2 and self.istmpupdate:
            el=self.environment.log[str(self.side*-1)]
            if len(el)>7:
                self.tmpestimate(el[len(el)-1-7:len(el)])
        if len(self.environment.actlist) == 1:  # 選択肢が一つしかないとき
            act = self.environment.actlist[0]
        elif self.mode == 1 and self.epsilon <= random():
            act = choice(self.environment.actlist)
            statesetlist, qr = self.qtable.qtableread(self.environment.state, self.side)
        else:
            statesetlist, qr = self.qtable.qtableread(self.environment.state, self.side)
            if statesetlist is not None:
                # n番目に強い選択肢の温度による選択確立推移
                # graph(statesetlist, len(self.environment.actlist))
                act = self.softmaxchoice(dict=statesetlist)
            else:
                act = self.stchoice()
        if self.mode == 1 and len(act) != 0 and len(self.environment.actlist) > 1:
            self.log.append([self.turn, self.environment.actlist, act, qr, statesetlist, copy(self.environment.state)])
        self.turn += 2
        return act
    def tmpestimate(self,el):
        tmp=[0.001,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1]
        klists=[]
        vlists=[]
        alist=[]
        for l in el:
            alist.append(str(l[0]))
            qt=self.qtable.qtableread(l[1], self.side*-1)[0]
            if qt is None:
                stli = {}
                state = np.where(l[1] > 1, 0, l[1])
                for i in range(SIZE):
                    for j in range(SIZE):
                        if state[i][j] == BLANK:
                            s, dif = cf.reversestones(index=[i, j], side=self.side*-1, instate=state)
                            if dif != 0:
                                stli[str([i, j])] = s
                score = []
                for st in stli.values():
                    point = 0
                    s = cf.makeactivemass(state=st, side=self.side)
                    for i in self.not_priority_action:
                        if s[i[0]][i[1]] == 2:
                            point += 1
                    for i in self.priority_action:
                        if s[i[0]][i[1]] == 2:
                            point -= 6
                    score.append(point)
                klists.append(list(stli.keys()))
                vlists.append(score)
            else:
                klists.append(list(qt.keys()))
                vlists.append([qt[k][1] for k in list(qt.keys())])
        tmpplist=[]
        for i, x in enumerate(tmp):
            li = []
            for klist,vlist in zip(klists,vlists):
                plist = cf.probabilityfunc(vlist=vlist, tmp=x)
                li.append(plist)
            matchcount=0
            for count in range(1000):
                pact=[]
                for l,k in zip(li,klists):
                    pact.append(k[npchoice(list(range(len(k))), p=l)])
                n=0
                for al,pa in zip(alist,pact):
                    if al==pa:
                        n+=1
                matchcount+=n/len(alist)
            tmpplist.append(matchcount)



        print("sum")
        print(tmpplist)
        t1=tmp[tmpplist.index(max(tmpplist))]
        t2=tmp[tmpplist.index(sorted(tmpplist)[-2])]
        print(t1)
        print(t2)









        #self.qtable.qtableread(i[1], self.side)[0]
    def softmaxchoice(self, dict):
        klist = list(dict.keys())
        vlist = [dict[k][1] for k in klist]
        plist = cf.probabilityfunc(vlist=vlist, tmp=self.temperature)
        m = klist[npchoice(list(range(len(klist))), p=plist)]
        return [int(m[1]), int(m[-2])]

    def stchoice(self):
        score = []
        for act in self.environment.actlist:
            st, _ = cf.reversestones(index=act, side=self.side, instate=self.environment.state)
            score.append(-1 * self.qtable.getstatevalue(st,self.side*-1))
        plist = cf.probabilityfunc(vlist=score, tmp=self.temperature)
        m = self.environment.actlist[npchoice(list(range(len(self.environment.actlist))), p=plist)]
        return m

    def save(self, reword):  # dict[ターン数][石値合計][選択肢の数]=[[state,{行動:[試行回数,行動価値] ...}],...]
        # [self.turn, self.environment.actlist, act, qr, statesetlist, copy(self.environment.state)]
        for t, step in enumerate(self.log):
            r = reword * self.gamma ** (len(self.log) - (t + 1))
            if step[4] is not None:
                q = step[4][str(step[2])]
                q += [1, (r - q[1]) / (q[0] + 1)]
                self.qtable.qtablesave(step[3], step[4], self.side)
            else:
                ql = {}
                for a in step[1]:
                    ql[str(a)] = np.array([0, 0], dtype=np.float32)
                ql[str(step[2])] += [1, r]
                self.qtable.qtablesave(step[3], ql, self.side)
            self.qtable.tablesave(step[5], r, self.side)


def basictraining(env, agentw, agentb, episode):
    for count in range(episode):
        env.reset()
        while env.winner is None:
            if env.side == WHITE:
                env.action(agentw.action())
            else:
                env.action(agentb.action())
        winner = env.winner
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
def basictest(env,agentw,agentb,set):
    wwin = 0
    bwin = 0
    draw = 0
    n = 0
    for count in range(set):
        env.reset()
        while env.winner is None:
            if env.side == WHITE:
                env.action(agentw.action())
            else:
                env.action(agentb.action())
        winner = env.winner
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

def train(episode, qtb):
    env = environment.Environment(SIZE)
    agentw = Agent(side=WHITE, mode=1, env=env, qtable=qtb, tmp=0.001)
    agentb = Agent(side=BLACK, mode=1, env=env, qtable=qtb, tmp=0.001)
    basictraining(env=env,agentb=agentb,agentw=agentw,episode=episode)


def trainb(episode, qtb):
    env = environment.Environment(SIZE)
    agentw = Agent2(side=BLACK, env=env, isforeseeing=False, issave=True)
    agentb = Agent(side=BLACK, mode=1, env=env, qtable=qtb, tmp=0.001)
    basictraining(env=env,agentb=agentb,agentw=agentw,episode=episode)


def trainw(episode, qtb):
    env = environment.Environment(SIZE)
    agentw = Agent(side=WHITE, mode=1, env=env, qtable=qtb, tmp=0.001)
    agentb = Agent2(side=BLACK, env=env, isforeseeing=False, issave=True)
    basictraining(env=env,agentb=agentb,agentw=agentw,episode=episode)


def train2(episode, qtb):
    env = environment.Environment(SIZE)
    agentw = Agent2(side=WHITE, env=env, qtable=qtb, issave=True)
    agentb = Agent2(side=BLACK, env=env, isforeseeing=False, issave=True)
    basictraining(env=env,agentb=agentb,agentw=agentw,episode=episode)
    agentw = Agent2(side=BLACK, env=env, isforeseeing=False, issave=True)
    agentb = Agent2(side=WHITE, env=env, qtable=qtb, issave=True)
    basictraining(env=env,agentb=agentb,agentw=agentw,episode=episode)


def test(whiteside, blackside, set):
    env = environment.Environment(SIZE)
    tmp = 0.001
    if whiteside:
        agentw = Agent(side=WHITE, mode=2, env=env, tmp=tmp)
    else:
        agentw = Agent2(side=WHITE, env=env)
    if blackside:
        agentb = Agent(side=BLACK, mode=2, env=env, tmp=tmp)
    else:
        agentb = Agent2(side=BLACK, env=env)
    return basictest(env=env,agentb=agentb,agentw=agentw,set=set)


# 温度の推移見る用
def test2(env=None, agentw=None, agentb=None, istmp=False):
    x, y1, y2 = [], [], []
    if env is None:
        env = environment.Environment(SIZE)
    if agentw is None:
        agentw = Agent(side=WHITE, mode=2, env=env, tmp=0.5)
    if agentb is None:
        agentb = Agent(side=BLACK, mode=2, env=env, tmpupdate=True)
    env.reset()
    while env.winner is None:
        if env.side == WHITE:
            env.action(agentw.action())
        else:
            env.action(agentb.action())
        if istmp:
            x.append(env.turn)
            y1.append(agentb.temperature)
            y2.append(agentw.temperature)
    winner = env.winner
    agentw.reset()
    agentb.reset()
    if istmp:
        plt.plot(x, y1)
        plt.plot(x, y2)
        plt.show()
    if winner == WHITE:
        return WHITE
    elif winner == BLACK:
        return BLACK
    else:
        return BLANK


def test3():
    x, y = [], []
    env = environment.Environment(SIZE)
    for tmp in range(1, 60):
        bwin = 0
        agentb = Agent(side=BLACK, mode=2, env=env, tmp=tmp * 0.01)
        agentw = Agent2(side=WHITE, env=env, isforeseeing=False)
        for count in range(1000):
            env.reset()
            while env.winner is None:
                if env.side == WHITE:
                    env.action(agentw.action())
                else:
                    env.action(agentb.action())
            winner = env.winner
            if winner == BLACK:
                bwin += 1
            agentb.reset()
        x.append(tmp * 0.01)
        y.append(bwin / 1000)
        print(bwin / 1000)
    plt.plot(x, y)
    plt.show()


def vsplayer(whiteside=False, blackside=False):
    env = environment.Environment(SIZE)
    print(env.side)
    def gui():
        root = tk.Tk()
        envgui.EnvGUI(env=env, master=root)

    thread1 = threading.Thread(target=gui)
    thread1.start()
    agentw = Agent(side=WHITE, mode=2, env=env, tmp=0.001)
    agentb = Agent(side=BLACK, mode=2, env=env, tmp=0.001)
    #agentw = Agent2(side=WHITE,  env=env,isforeseeing=False)
    #agentb = Agent2(side=BLACK, env=env,isforeseeing=False)
    while env.winner is None:
        if env.side == WHITE:
            if not whiteside:
                env.action(agentw.action())
            else:
                turn = env.turn
                while not os.path.isfile(str(turn) + ".pkl"):
                    time.sleep(0.001)
                time.sleep(0.001)
                with open(str(turn) + ".pkl", 'rb') as f:
                    data = pickle.load(f)
                env.action(data)
                os.remove(str(turn) + ".pkl")
        else:
            if not blackside:
                env.action(agentb.action())
            else:
                turn = env.turn
                while not os.path.isfile(str(turn) + ".pkl"):
                    time.sleep(0.001)
                time.sleep(0.001)
                with open(str(turn) + ".pkl", 'rb') as f:
                    data = pickle.load(f)
                env.action(data)
                os.remove(str(turn) + ".pkl")
    winner = env.winner
    if winner == WHITE:
        print("白の勝ち")
    elif winner == BLACK:
        print("黒の勝ち")
    else:
        print("引き分け")
    thread1.join()


def t():
    qtb = qtable.Qtable()
    logs = log.LOG(SIZE)
    testset = 100
    trainset = 10000
    # _, bwin, _, n = test(whiteside=False, blackside=True, set=testset)
    # logs.save(bwin / n, 0)
    for i in range(5):
        s = time.perf_counter()
        print("training...")
        train2(trainset, qtb)
        print("test...")
        _, bwin, _, n = test(whiteside=False, blackside=True, set=testset)
        e = time.perf_counter()
        print(e - s)
        logs.save(bwin / n, trainset)
    print("save")
    # qtb.finalsave()
    logs.end()



def t2():
    qtb = qtable.Qtable()
    logs = log.LOG(SIZE)
    testset = 100
    trainset = 10000
    # _, bwin, _, n = test(whiteside=False, blackside=True, set=testset)
    # logs.save(bwin / n, 0)
    for i in range(5):
        s = time.perf_counter()
        print("training...")
        trainb(trainset, qtb)
        trainw(trainset, qtb)
        print("test...")
        _, bwin, _, n = test(whiteside=False, blackside=True, set=testset)
        e = time.perf_counter()
        print(e - s)
        logs.save(bwin / n, trainset)
    print("save")
    # qtb.finalsave()
    logs.end()

if __name__ == "__main__":

    #vsplayer(blackside=True)
    # print(test2(istmp=True))
    s = time.perf_counter()
    t()
    t2()
    #test3()
    #test(whiteside=False, blackside=True, set=10)
    e = time.perf_counter()
    print(e - s)
    # plt.show()
    # 一試合での温度推移確認
    #test2()
    # 温度による勝率推移確認
    # test3()
