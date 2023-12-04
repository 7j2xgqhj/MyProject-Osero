import datetime
import os
import random
from agent2 import Agent2
import numpy as np
import commonfunc as cf
import environment
import netlearning as net
import pickle
from parameter import Parameter
from multiprocessing import Process
SIZE= Parameter.SIZE
BLANK = 0  # 石が空：0
BLACK = 1  # 石が黒：1
WHITE = -1  # 石が白：2
Path=os.path.abspath("..\\..\\qcash") + "/t/"
Path2=os.path.abspath("..\\..\\qcash") + "/t2/"
Path3=os.path.abspath("..\\..\\qcash") + "/t3/"
class Environment2:
    # 初期化
    def __init__(self, startset):
        self.startset=startset
        self.size = int(SIZE)  # 8 or 6 or 4
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
    def getstartset(self):
        return [self.state, self.side, self.winner, self.isPassed,self.turn]
def saveval(startset,l):
    state=startset[0]
    a = np.where(state > 1, 0, state)
    s=[]
    t=[]
    if l[0]+l[1] !=0:
        v=l[0]/(l[0]+l[1])-0.5
    else:
        v=0
    for x in range(2):
        for y in range(4):
            if x == 1:
                sou = np.fliplr(a)
            else:
                sou = a
            sou = np.rot90(sou, y)
            sou=sou.ravel()
            s.append(sou.tolist())
            t.append(v)
    statestr = ""
    for i in state:
        for j in i:
            statestr += str(j + 1)
    with open(Path2 + statestr + ".pkl", 'wb') as f:
        pickle.dump([s,t], f)
def boardvalue(startset):
    wwin = 0
    bwin = 0
    draw = 0
    se=200
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
def boardvalue2(startset):
    wwin = 0
    bwin = 0
    draw = 0
    env=Environment2(startset)
    for act in env.actlist:
        if env.side == WHITE:
            env.action(act)
        else:
            env.action(act)
        winner = env.winner
        if winner == WHITE:
            wwin += 1
        elif winner == BLACK:
            bwin += 1
        elif winner ==BLANK:
            draw += 1
        else:
            pbwin,pwwin,pdraw =boardvalue2(env.getstartset())
            bwin+=pbwin
            wwin+=pwwin
            draw+=pdraw
    saveval(startset,[bwin,wwin,draw])
    return bwin,wwin,draw
def makedata():
    for i in range(10):
        env = environment.Environment()
        s = []
        t = []
        agentw=Agent2(side=WHITE, env=env, issave=True)
        agentb=Agent2(side=BLACK, env=env, issave=True)
        for count in range(200):
            print(str(count+1)+"/200 & "+str(i)+"/10")
            f = random.randint(SIZE, SIZE**2-5)
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
        st=random.randint(0,1000)

        with open(Path+dt_now.strftime('%Y%m%d%H%M%S')+str(st)+".pkl", 'wb') as f:
            pickle.dump([s,t], f)
def multimakedata():
    p = Process(target=makedata)
    p.start()
    p = Process(target=makedata)
    p.start()
    p = Process(target=makedata)
    p.start()
def checkdata():
    print("ttt")
    flag=False
    env = environment.Environment()
    agentw = Agent2(side=WHITE, env=env, issave=True)
    agentb = Agent2(side=BLACK, env=env, issave=True)
    c=0
    miss=[]
    for count in range(100):
        f = random.randint(SIZE, SIZE**2-5)
        env.reset()
        while env.winner is None:
            if f == env.turn:
                a = env.state.flatten()
                a = np.where(a > 1, 0, a)
                n=net.getval(a.tolist())[0][0]
                b=boardvalue([env.state, env.side, env.winner, env.isPassed,env.turn])
                if n*b<0:
                    c+=1
                    miss.append([f,n,b])
                    flag =True
            if env.side == WHITE:
                env.action(agentw.action())
            else:
                env.action(agentb.action())
        agentw.reset()
        agentb.reset()
    print("100問中"+str(100-c)+"問正解")
    print("間違えた回")
    for i in miss:
        print(str(i[0])+"手目:net "+str(i[1])+":board "+str(i[2]))
    return flag
def learn():
    li=os.listdir(Path3)
    for l in li:
        with open(Path3+l, 'rb') as f:
            data = pickle.load(f)
        net.netlearning(data[0],data[1])
def saveop():
    li=os.listdir(Path2)
    n = 100
    for i in range(0, len(li), n):
        s=[]
        t=[]
        for l in li[i: i + n]:
            with open(Path2 + l, 'rb') as f:
                data = pickle.load(f)
            for state ,target in zip(data[0],data[1]):
                s.append(state)
                t.append([target])
            os.remove(Path2 + l)
        dt_now = datetime.datetime.now()
        st = random.randint(0, 1000)
        with open(Path3 + dt_now.strftime('%Y%m%d%H%M%S') + str(st) + ".pkl", 'wb') as f:
            pickle.dump([s, t], f)

def tes():
    env=environment.Environment()
    for count in range(100):
        f = random.randint(35, 55)
        env.reset()
        print(f)
        print(count)
        while env.winner is None:
            if f == env.turn:
                boardvalue2([env.state, env.side, env.winner, env.isPassed, env.turn])
            if env.side == WHITE:
                env.action(random.choice(env.actlist))
            else:
                env.action(random.choice(env.actlist))
    saveop()
    learn()
if __name__ == '__main__':
    tes()
    #saveop()
    #multimakedata()
    #learn()
    #checkdata()
    #multimakedata()

