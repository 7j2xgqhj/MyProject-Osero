import numpy as np
import environment
import random
import matplotlib.pyplot as plt
import math
import time

BLANK = 0  # 石が空：0
BLACK = 1  # 石が黒：1
WHITE = -1  # 石が白：2

SIZE = 4
GAMMA = 0.9  # 割引率
EPSILON = 0.8
ATTENUATION = EPSILON / 80  # 減衰率
TEMPERATURE =1#温度定数初期値    上げると等確率　下げると強調　加算減算ではなく比で考えて調整するのがいいかも
EPTEMPERATURE=0.4

WINREWORD=1
LOSEREWORD=-1
DRAWREWORD=-0.5

class Agent:
    # 盤面の情報は、先手・後手(定数)、何手目(計算が簡単)、石値合計(np.sum(state))。打てる手数(ついでで使える)で分類して絞り込めるようにすることで計算時間を削減したい
    def __init__(self, side, dict):
        self.side = side
        self.tables = dict
        self.log = []
        self.gamma = GAMMA
        self.epsilon = EPSILON
        self.temperature=TEMPERATURE
        if side == BLACK:
            self.turn = 0
        elif side == WHITE:
            self.turn = 1

    def reset(self):
        self.epsilon = EPSILON
        self.log = []
        self.temperature = TEMPERATURE
        if self.side == BLACK:
            self.turn = 0
        elif self.side == WHITE:
            self.turn = 1

    def action(self, state, actlist, islearn=None):  ##testとtrainをまとめたい　方策と記録のとこだけ変える
        if len(actlist) == 1:  # 選択肢が一つしかないとき
            act = actlist[0]
        else:
            key1 = str(self.turn)
            key2 = str(np.sum(state))
            key3 = str(len(actlist))
            # テーブルにターン数・行動候補数の記録がある
            if key1 in self.tables and key2 in self.tables[key1] and key3 in self.tables[key1][key2]:
                statesetlist = self.tables[key1][key2][key3]
                statelist = [i[0] for i in statesetlist]
                # テーブルにおいて、現在の盤面と一致する盤面が存在する場合そのindexを求める
                indexl = []
                indexl = [i for i, x in enumerate(statelist) if np.all(x == state)]
                # 現在の盤面と一致する盤面が存在するとき
                if len(indexl) == 1:
                    if islearn != None:
                        if islearn:
                            act = self.epsilongreedy(dict=statesetlist[indexl[0]][1], actlist=actlist)
                        else:
                            act = self.softmaxchoice(dict=statesetlist[indexl[0]][1], actlist=actlist)
                    else:
                        act = self.maxreword(dict=statesetlist[indexl[0]][1], actlist=actlist)
                else:
                    act = random.choice(actlist)
            else:
                act = random.choice(actlist)
        if islearn:
            self.log.append([self.turn, actlist, act, state])
            self.epsilon -= ATTENUATION
        self.turn += 2
        return act

    def epsilongreedy(self, dict, actlist):  # dictは行動候補辞書{行動候補:[試行回数,行動価値]}
        if self.epsilon > random.random():
            set = [[a, dict[str(a)][1]] for a in actlist]
            act = random.choice([i[0] for i in set if i[1] == max([i[1] for i in set])])
        else:
            vlist = [dict[str(a)][1] for a in actlist]
            q = [np.exp(a / EPTEMPERATURE) for a in vlist]
            plist = [qa / sum(q) for qa in q]
            act = actlist[np.random.choice(list(range(len(actlist))), p=plist)]
        return act

    def maxreword(self, dict, actlist):
        set = [[a, dict[str(a)][1]] for a in actlist]
        act = random.choice([i[0] for i in set if i[1] == max([i[1] for i in set])])
        return act
    def softmaxchoice(self, dict, actlist):
        vlist = [dict[str(a)][1] for a in actlist]
        q = [np.exp(a / self.temperature) for a in vlist]
        plist=[qa/sum(q) for qa in q]
        act = actlist[np.random.choice(list(range(len(actlist))), p=plist)]
        return act
    def save(self, reword):  # dict[ターン数][石値合計][選択肢の数]=[[state,{行動:[試行回数,行動価値] ...}],...]
        # step[0]:ターン数、step[1]:選択肢の配列、step[2]:選択した行動、step[3]:盤面(ndarray)
        for t, step in enumerate(self.log):
            # 割引現在価値
            r = reword * self.gamma ** (len(self.log) - (t + 1))
            key1 = str(step[0])
            key2 = str(np.sum(step[3]))
            key3 = str(len(step[1]))
            key4 = str(step[2])
            state = step[3]
            if not key1 in self.tables:
                self.tables[key1] = {}
            if not key2 in self.tables[key1]:
                self.tables[key1][key2] = {}
            # 一致する行動候補数の記録がない
            if not key3 in self.tables[key1][key2]:
                self.tables[key1][key2][key3] = []
            # 絞り込んだ盤面の候補の中から一致する盤面のインデックスを返す
            statesetlist = self.tables[key1][key2][key3]
            statelist = [i[0] for i in statesetlist]
            index = [i for i, x in enumerate(statelist) if np.all(x == state)]
            if len(index) == 1:  # 一致する盤面が見つかった時
                dict = self.tables[key1][key2][key3][index[0]][1]
                if dict[key4][0] != 0:
                    dict[key4] += [1, (r - dict[key4][1]) / dict[key4][0]]
                else:
                    dict[key4] += [1, r]
            else:  # 盤面が一致しなかったとき
                # 盤面の記録
                dict = {}
                # その盤面で取れる行動の候補を記録　初期化
                for a in step[1]:
                    dict[str(a)] = np.array([0, 0], dtype=float)  # keyは"x,y" ここでnp配列で初期化している
                dict[key4] += [1, r]  # 取った行動の記録
                self.tables[key1][key2][key3].append([state, dict])
            self.tables['count'] += 1

    def savedict(self):
        if self.side == BLACK:
            np.save('tableblack.npy', self.tables)
        elif self.side == WHITE:
            np.save('tablewhite.npy', self.tables)

    def getfirststep(self):
        dict = self.tables['2']
        print(dict)


def train(episode):
    dictw = np.load('tablewhite.npy', allow_pickle=True).item()
    dictb = np.load('tableblack.npy', allow_pickle=True).item()
    agentw = Agent(side=WHITE, dict=dictw)
    agentb = Agent(side=BLACK, dict=dictb)
    env = environment.Environment(SIZE)
    for count in range(episode):
        env.reset()
        while env.getwinner().size == 0:
            state = env.getstate()
            actlist = env.actlist
            if env.side == WHITE:
                act = agentw.action(state=state, actlist=actlist, islearn=True)
            else:
                act = agentb.action(state=state, actlist=actlist, islearn=True)
            # time.sleep(10)
            env.action(act)
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
    agentb.savedict()
    agentw.savedict()
    # agentb.getfirststep()


def test(whiteside, blackside, set):
    dictw = np.load('tablewhite.npy', allow_pickle=True).item()
    dictb = np.load('tableblack.npy', allow_pickle=True).item()
    wwin = 0
    bwin = 0
    draw = 0
    n = 0
    env = environment.Environment(SIZE)
    agentw = Agent(side=WHITE, dict=dictw)
    agentb = Agent(side=BLACK, dict=dictb)
    scoreB = 0
    scoreW = 0
    for count in range(set):
        env.reset()
        while env.getwinner().size == 0:
            actlist = env.actlist
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
        else:
            draw += 1
        n += 1
        agentw.reset()
        agentb.reset()
    print("Wwin:" + str(wwin)+"回")
    print("Bwin:" + str(bwin)+"回")
    print("draw:"+str(draw)+"回")
    print("総試合数:" + str(n)+"回")
    return [wwin,bwin,draw,n]


def resetW():
    np.save('tablewhite.npy', np.array({'count': 0}))


def resetB():
    np.save('tableblack.npy', np.array({'count': 0}))


def dictcheckW():
    dictw = np.load('tablewhite.npy', allow_pickle=True).item()
    print(dictw)


if __name__ == "__main__":
    resetB()
    resetW()
    num=0
    x=[0]
    y=[test(whiteside=False, blackside=True, set=1000)[1]]
    for i in range(40):
        train(100)
        num+=100
        x.append(num)
        y.append(test(whiteside=False, blackside=True, set=1000)[1])
    plt.plot(x, y)
    plt.show()

#    for i in range(5):
#       cnum = num
#      for j in range(9):
#         print("追加" + str(cnum)+"回の訓練")
#        train(cnum)
#       num += cnum
#      print("合計" + str(num)+"回の訓練")
#     test(whiteside=False, blackside=True, set=100)
