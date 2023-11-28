import datetime
import os
import random
from agent2 import Agent2
import numpy as np
import commonfunc as cf
from random import choice
import environment
import test
import pickle
BLANK = 0  # 石が空：0
BLACK = 1  # 石が黒：1
WHITE = -1  # 石が白：2


class Environment2:
    # 初期化
    def __init__(self, startset):
        self.startset=startset
        self.size = int(8)  # 8 or 6 or 4
        self.reset()

    def reset(self):
        self.state,self.side, self.winner, self.isPassed,self.turn = self.startset
        self.actlist=[]
        self.makeactlist()

    def turn_change(self):
        self.side *= -1

    # self.actlistを更新
    def makeactlist(self):
        ind = []
        stli={}
        n=2
        self.state = np.where(self.state > 1, 0, self.state)
        for i in range(self.size):
            for j in range(self.size):
                if self.state[i][j] == BLANK:
                    s, dif = cf.reversestones(index=[i, j],side=self.side,instate=self.state)
                    if dif != 0:
                        ind.append([[i, j], n])
                        stli[str([i,j])]=s
                        n+=1
        for i in ind:
            self.state[i[0][0]][i[0][1]] = i[1]
        self.statelist=stli
        actlist=[]
        for i in range(2,n):
            id=np.where(self.state == i)
            actlist.append([id[0][0],id[1][0]])
        self.actlist = actlist
        if len(self.actlist)==0:
            self.actlist.append([])

    # 行動をする。成功したらTrue、失敗ならFalseを返す
    def action(self, act):
        if act in self.actlist:
            if len(act) == 0:
                if self.isPassed:
                    self.decidewinner()
                else:
                    self.isPassed = True
            else:
                self.state, self.isPassed = cf.reversestones(index=act,side=self.side,instate=self.state)[0], False
            self.turn_change()
            self.turn += 1
            self.makeactlist()
            return True
        else:
            return False

    def decidewinner(self):
        white, black = np.count_nonzero(self.state == WHITE), np.count_nonzero(self.state == BLACK)
        w = max(white, black)
        if white == black:
            self.winner = BLANK
        else:
            if white == w:
                self.winner = WHITE
            elif black == w:
                self.winner = BLACK
def boardvalue(startset):
    wwin = 0
    bwin = 0
    draw = 0
    se=1000
    env=Environment2(startset)
    agentw = Agent2(side=WHITE, env=env, issave=True)
    agentb = Agent2(side=BLACK, env=env, issave=True)
    for count in range(se):
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
        agentw.reset()
        agentb.reset()
    return bwin/(se-draw)-0.5
def l():
    for i in range(10):
        env = environment.Environment()
        s = []
        t = []
        agentw=Agent2(side=WHITE, env=env, issave=True)
        agentb=Agent2(side=BLACK, env=env, issave=True)
        for count in range(100):
            f = random.randint(35, 55)
            env.reset()
            while env.winner is None:
                if f == env.turn:
                    a = np.where(env.state > 1, 0, env.state)
                    v=[boardvalue([env.state, env.side, env.winner, env.isPassed,env.turn])]
                    for x in range(2):
                        for y in range(4):
                            if x == 1:
                                sou = np.fliplr(a)
                            else:
                                sou=a
                            sou = np.rot90(sou, y)
                            sou.ravel()
                            s.append(sou.tolist())
                            t.append(v)
                if env.side == WHITE:
                    env.action(agentw.action())
                else:
                    env.action(agentb.action())
            agentw.reset()
            agentb.reset()
        dt_now = datetime.datetime.now()
        with open(os.path.abspath("..\\..\\qcash") + "/t/"+dt_now.strftime('%Y%m%d%H%M%S')+".pkl", 'wb') as f:
            pickle.dump([s,t], f)
        print("net")
        test.netlearning(s, t)
        print("netend")
def ttt():
    print("ttt")
    flag=False
    env = environment.Environment()
    agentw = Agent2(side=WHITE, env=env, issave=True)
    agentb = Agent2(side=BLACK, env=env, issave=True)
    for count in range(10):
        f = random.randint(35, 55)
        env.reset()
        while env.winner is None:
            if f == env.turn:
                a = env.state.flatten()
                a = np.where(a > 1, 0, a)
                n=test.getval(a.tolist())[0]
                b=boardvalue([env.state, env.side, env.winner, env.isPassed,env.turn])
                if n*b<0:
                    flag =True
            if env.side == WHITE:
                env.action(agentw.action())
            else:
                env.action(agentb.action())
        agentw.reset()
        agentb.reset()
    return flag

count=0
while ttt() or count==30:
    print(count)
    l()
    count+=1