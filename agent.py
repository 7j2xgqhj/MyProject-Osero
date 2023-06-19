import numpy as np
import environment
import random
import math
import time
from multiprocessing import Process
from multiprocessing import Manager

BLANK = 0  # 石が空：0
BLACK = 1  # 石が黒：1
WHITE = 2  # 石が白：2



class Agent:
    # 盤面の情報は、先手・後手(定数)、何手目(計算が簡単)、打てる手数(ついでで使える)で分類して絞り込めるようにすることで計算時間を削減したい
    # クラス生成→並列処理→全処理終了後saveが理想？
    # どのみち同じエージェント同士で対局させるのでtrainとかtestもクラス内部でいいのでは？
    # 並列処理の問題は、クラス生成→並列処理→全処理終了後saveでやると、並列処理中のresetが邪魔
    # resetの干渉を避けるために、クラス生成の時点から並列化したいが、並列化するとalllogが分かれるためsave時に並列化した処理の記録同士が上書きし合う
    # alllogを共通化するために、外部から参照渡しを使用する。
    # ややこしくなってきたのでもう全部外に出す
    def __init__(self, side, dict):
        self.side = side
        self.tables = dict
        if side == BLACK:
            self.turn = 0
        elif side == WHITE:
            self.turn = 1

    def reset(self):
        if self.side == BLACK:
            self.turn = 0
        elif self.side == WHITE:
            self.turn = 1

    def action(self, state, actlist):
        if len(actlist) == 1:  # 選択肢が一つしかないとき
            act = actlist[0]
        else:
            # テーブルにターン数・行動候補数の記録がある
            if str(self.turn) in self.tables and str(len(actlist)) in self.tables[str(self.turn)]:
                statesetlist = self.tables[str(self.turn)][str(len(actlist))]
                statelist = [i[0] for i in statesetlist]
                # テーブルにおいて、現在の盤面と一致する盤面が存在する場合そのindexを求める
                indexl = [i for i, x in enumerate(statelist) if np.array_equal(i, state)]
                # 現在の盤面と一致する盤面が存在するとき
                if len(indexl) == 1:
                    act = self.uct(dict=statesetlist[indexl[0]][1], actlist=actlist)
                    # ここでUCB1 (勝利回数/その選択の試行回数)+√2*√(log(全体の試行回数)/その選択の試行回数)
                else:
                    act = random.choice(actlist)
            else:
                act = random.choice(actlist)
        self.turn += 2
        return act

    def uct(self, dict, actlist):  # dictは行動候補辞書{行動候補:[試行回数,勝利回数]}
        n = sum([i[0] for i in list(dict.values())])
        actset = []
        for a in actlist:
            t, w = dict[str(a[0]) + "," + str(a[1])]
            ucb = (w / t + math.sqrt(2) * math.sqrt(math.log(n) / t))
            actset.append([a, ucb])
        ucblist = [i[1] for i in actset]
        return actset[ucblist.index(max(ucblist))][0]


def save(alllog, side, dicta):  # {何手目:{その時の行動候補数:[state,{行動:[試行回数,勝利回数]}]}}の構成
    tables = dicta
    for logs in alllog:
        tables['count']+=1
        log = logs[0]
        iswin = logs[1]
        reword = 0
        if iswin:
            reword += 1
        # stepは[ターン数, 行動候補, 取った行動, その時の盤面]
        for step in log:
            if not str(step[0]) in tables:
                tables[str(step[0])] = {}
            # 一致する行動候補数の記録がない
            if not str(len(step[1])) in tables[str(step[0])]:
                tables[str(step[0])][str(len(step[1]))] = []
            index = [j for j, x in enumerate([i[0] for i in tables[str(step[0])][str(len(step[1]))]]) if
                     np.array_equal(j, step[3])]
            if len(index) == 1:  # 一致する盤面が見つかった時
                dict = tables[str(step[0])][str(len(step[1]))][index]
                dict[str(step[2][0]) + "," + str(step[2][1])] += [1, reword]
            else:  # 盤面が一致しなかったとき
                stateset = tables[str(step[0])][str(len(step[1]))]  # 盤面の記録
                dict = {}
                # その盤面で取れる行動の候補を記録　初期化
                for a in step[1]:
                    dict[str(a[0]) + "," + str(a[1])] = np.array([0, 0])  # keyは"x,y"
                dict[str(step[2][0]) + "," + str(step[2][1])] += [1, reword]  # 取った行動の記録
                stateset.append([step[3], dict])
    if side == BLACK:
        np.save('tableblack.npy', tables)
    elif side == WHITE:
        np.save('tablewhite.npy', tables)


def ep(dicts, alllogs,c):
    logw = []
    logb = []
    dictw = dicts[0]
    dictb = dicts[1]
    alllogw = alllogs[0]
    alllogb = alllogs[1]
    agentw = Agent(side=WHITE, dict=dictw)
    agentb = Agent(side=BLACK, dict=dictb)
    env = environment.Environment()
    for count in range(c):
        env.reset()
        while env.getwinner().size == 0:
            turn = env.getturn()
            state = env.getstate()
            actlist = env.actlist
            if env.side == WHITE:
                act = agentw.action(state=state, actlist=actlist)
                env.action(act)
                if len(actlist) > 1:
                    logw.append([turn, actlist, act, state])
            else:
                act = agentb.action(state=state, actlist=actlist)
                env.action(act)
                if len(actlist) > 1:
                    logb.append([turn, actlist, act, state])
        winner = env.getwinner()
        if winner == WHITE:
            agentw.reset()
            logw = [logw, True]
            logb = [logb, False]
            agentb.reset()
        elif winner == BLACK:
            logw = [logw, False]
            logb = [logb, True]
            agentw.reset()
            agentb.reset()
        else:
            logw = [logw, False]
            logb = [logb, False]
            agentw.reset()
            agentb.reset()

        alllogw.append(logw)
        alllogb.append(logb)


def train(episode):
    manager = Manager()
    dictw = np.load('tablewhite.npy', allow_pickle=True).item()
    dictb = np.load('tableblack.npy', allow_pickle=True).item()
    alllogw = manager.list([])
    alllogb = manager.list([])
    core = 2
    c=int(round(episode/2))
    p1 = Process(target=ep, args=([dictw, dictb], [alllogw, alllogb], c))
    p2 = Process(target=ep, args=([dictw, dictb], [alllogw, alllogb], c))
    # p = [multiprocessing.Process(target=ep,args=([dictw,dictb],[alllogw,alllogb],episode,core)) for i in range(core)]
    # [p[i].start() for i in range(core)]
    # [p[i].join() for i in range(core)]
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    save(alllog=alllogb, side=BLACK, dicta=dictb)
    save(alllog=alllogw, side=WHITE, dicta=dictw)


def test(whiteside, blackside, set):
    dictw = np.load('tablewhite.npy', allow_pickle=True).item()
    dictb = np.load('tableblack.npy', allow_pickle=True).item()
    wwin = 0
    bwin = 0
    n = 0
    env = environment.Environment()
    agentw = Agent(side=WHITE, dict=dictw)
    agentb = Agent(side=BLACK, dict=dictb)
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
        n += 1
    print("Wwin" + str(wwin))
    print("Bwin" + str(bwin))
    print("総試合数" + str(n))


def resetW():
    np.save('tablewhite.npy', np.array({'count':0}))


def resetB():
    np.save('tableblack.npy', np.array({'count':0}))


def dictcheckW():
    dictw = np.load('tablewhite.npy', allow_pickle=True).item()
    print(dictw)


if __name__ == "__main__":
    resetB()
    resetW()
    for i in range(1):
        t_s = time.perf_counter()
        train(1000)
        test(whiteside=False, blackside=True, set=100)
        t_e = time.perf_counter()
        print(t_e - t_s)
