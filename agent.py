import numpy as np
import environment
import random
import math

BLANK = 0  # 石が空：0
BLACK = 1  # 石が黒：1
WHITE = 2  # 石が白：2


class Agent:
    # 盤面の情報は、先手・後手(定数)、何手目(計算が簡単)、打てる手数(ついでで使える)で分類して絞り込めるようにすることで計算時間を削減したい
    def __init__(self, side, learn):
        self.side = side
        if side == BLACK:
            self.tables = np.load('tableblack.npy', allow_pickle=True).item()
            self.turn = 0
        elif side == WHITE:
            self.tables = np.load('tablewhite.npy', allow_pickle=True).item()
            self.turn = 1
        self.learn = learn
        self.log = []

    def action(self, state, actlist):
        if len(actlist) ==1:#選択肢が一つしかないとき　記録もしない
            act=actlist[0]
        else:
        #テーブルにターン数・行動候補数の記録がある
            if str(self.turn) in self.tables and str(len(actlist)) in self.tables[str(self.turn)]:
                statesetlist = self.tables[str(self.turn)][str(len(actlist))]
                statelist=[i[0] for i in statesetlist]
                #テーブルにおいて、現在の盤面と一致する盤面が存在する場合そのindexを求める
                indexl = [i for i, x in enumerate(statelist) if np.array_equal(i, state)]
                #現在の盤面と一致する盤面が存在するとき
                if len(indexl) == 1:
                    act = self.uct(dict=statesetlist[indexl[0]][1], actlist=actlist)
                    # ここでUCB1 (勝利回数/その選択の試行回数)+√2*√(log(全体の試行回数)/その選択の試行回数)
                else:
                    act = random.choice(actlist)
            else:
                act = random.choice(actlist)
            if self.learn:
                self.log.append([self.turn, actlist, act, state])
        self.turn += 2
        return act

    def uct(self, dict, actlist):#dictは行動候補辞書{行動候補:[試行回数,勝利回数]}
        n = sum([i[0] for i in list(dict.values())])
        actset = []
        for a in actlist:
            t, w = dict[str(a[0]) + "," + str(a[1])]
            ucb = (w / t + math.sqrt(2) * math.sqrt(math.log(n) / t))
            actset.append([a, ucb])
        ucblist = [i[1] for i in actset]
        return actset[ucblist.index(max(ucblist))][0]
    def save(self, iswin):  # {何手目:{その時の行動候補数:[state,{行動:[試行回数,勝利回数]}]}}の構成
        reword = 0
        if iswin:
            reword += 1
        # stepは[ターン数, 行動候補, 取った行動, その時の盤面]
        for step in self.log:
            if not str(step[0]) in self.tables:
                self.tables[str(step[0])] = {}
            # 一致する行動候補数の記録がない
            if not str(len(step[1])) in self.tables[str(step[0])]:
                self.tables[str(step[0])][str(len(step[1]))]=[]
            index=[j for j,x in enumerate([i[0] for i in self.tables[str(step[0])][str(len(step[1]))]]) if np.array_equal(j,step[3])]
            if len(index)==1:#一致する盤面が見つかった時
                dict = self.tables[str(step[0])][str(len(step[1]))][index]
                dict[str(step[2][0]) + "," + str(step[2][1])] += [1, reword]
            else:#盤面が一致しなかったとき
                stateset = self.tables[str(step[0])][str(len(step[1]))]# 盤面の記録
                dict={}
                #その盤面で取れる行動の候補を記録　初期化
                for a in step[1]:
                    dict[str(a[0]) + "," + str(a[1])] = [0, 0]  # keyは"x,y"
                dict[str(step[2][0]) + "," + str(step[2][1])] += [1, reword]  # 取った行動の記録
                stateset.append([step[3],dict])
        if self.side == BLACK:
            np.save('tableblack.npy', self.tables)
        elif self.side == WHITE:
            np.save('tablewhite.npy', self.tables)

def train(episode):
    for count in range(episode):
        for count in range(100):
            agentw = Agent(side=WHITE, learn=True)
            agentb = Agent(side=BLACK, learn=True)
            env = environment.Environment()
            while env.getwinner().size == 0:
                actlist = env.actlist()
                if env.side == WHITE:
                    env.action(agentw.action(state=env.getstate(), actlist=actlist))
                else:
                    env.action(agentb.action(state=env.getstate(), actlist=actlist))
            winner = env.getwinner()
            if winner == WHITE:
                agentw.save(True)
                agentb.save(False)
            elif winner == BLACK:
                agentw.save(False)
                agentb.save(True)
            else:
                agentw.save(False)
                agentb.save(False)

def test(whiteside,blackside,set):
    wwin = 0
    bwin = 0
    n=0
    for count in range(set):
        agentw = Agent(side=WHITE, learn=False)
        agentb = Agent(side=BLACK, learn=False)
        env = environment.Environment()
        while env.getwinner().size == 0:
            actlist = env.actlist()
            if env.side == WHITE:
                if whiteside:
                    env.action(agentw.action(state=env.getstate(), actlist=actlist))
                else:
                    env.action(random.choice(actlist))
            else:
                if blackside:
                    env.action(agentb.action(state=env.getstate(), actlist=actlist))
                else:
                    env.action(random.choice(actlist))
        winner = env.getwinner()
        if winner == WHITE:
            wwin += 1
        elif winner == BLACK:
            bwin += 1
        n+=1
    print("Wwin" + str(wwin))
    print("Bwin" + str(bwin))
    print("総試合数"+str(n))

def resetW():
    np.save('tablewhite.npy', np.array({}))
def resetB():
    np.save('tableblack.npy', np.array({}))

if __name__ == "__main__":
    resetB()
    resetW()
    train(10000)
    test(whiteside=False,blackside=True,set=10000)


