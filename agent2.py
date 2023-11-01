from numpy import copy
from random import choice
import numpy as np
from numpy import add
import qtable
from parameter import Parameter
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
VALUERATE=Parameter.VALUERATE



class Agent2:
    def __init__(self, side, env=None,isforeseeing=True,issave=False, qtable=qtable.Qtable()):
        self.environment = env
        self.side = side
        self.size=self.environment.size
        self.isforeseeing=isforeseeing
        self.issave=issave
        self.log=[]
        self.qtable = qtable
        self.priority_action=[[0,0],[0,self.size-1],[self.size-1,0],[self.size-1,self.size-1]]
        self.not_priority_action = [[1, 0], [1,0], [1,1],
                                    [0,self.size - 2],[1,self.size - 1],[1,self.size - 2],
                                    [self.size - 2,0],[self.size - 1,1],[self.size - 2,1],
                                    [self.size - 2,self.size - 1],[self.size - 1,self.size - 2],[self.size - 2,self.size - 2]]
        if side == BLACK:
            self.turn = 0
        elif side == WHITE:
            self.turn = 1
    def reset(self):
        self.log=[]
        if self.side == BLACK:
            self.turn = 0
        elif self.side == WHITE:
            self.turn = 1
    def action(self):
        if len(self.environment.actlist) <= 1:
            return self.environment.actlist[0]
        for a in self.priority_action:
            if a in self.environment.actlist:
                act=a
                if self.issave:
                    self.logmake(act)
                return act
        l=copy(self.environment.actlist).tolist()
        al=list(filter(lambda x: x not in self.not_priority_action, l))
        if len(al)>0 and not self.isforeseeing:
            act = choice(al)
            if self.issave:
                self.logmake(act)
            return act
        elif len(al)>0 and self.isforeseeing:
            score=[]
            for st in self.environment.statelist.values():
                point=0
                s=self.makeactivemass(st)
                for i in self.not_priority_action:
                    if s[i[0]][i[1]]==2:
                        point+=1
                for i in self.priority_action:
                    if s[i[0]][i[1]]==2:
                        point-=12
                score.append(point)
            if np.all(np.array(score)==score[0]):
                act=choice(self.environment.actlist)
                if self.issave:
                    self.logmake(act)
                return act
            else:
                act=self.environment.actlist[score.index(max(score))]
                if self.issave:
                    self.logmake(act)
                return act
        else:
            act=choice(self.environment.actlist)
            if self.issave:
                self.logmake(act)
            return act
    def makeactivemass(self,state):
        ind = []
        st=copy(state)
        for i in range(self.size):
            for j in range(self.size):
                if st[i][j] == BLANK:
                    s, dif = self.reversestones([i, j],st)
                    if dif != 0:
                        ind.append([i, j])
        for i in ind:
            st[i[0]][i[1]] = 2
        return st

    def reversestones(self, index,instate):  # 引数に座標、出力は変化後の盤面orダメだったらfalse
        side =self.side*-1
        arrayclone = copy(instate)  # 参照渡し対策　必須
        for i in [[0, -1], [1, -1], [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1]]:
            localindex, directon, returnstonelist, isdifferentcoloredstone = np.array(index,
                                                                                      dtype=np.int8), i, [], False
            localindex = add(localindex, directon)  # 各方向にひとつづつ進める
            while np.all(localindex >= 0) and np.all(localindex < self.size):
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
                localindex = add(localindex, directon)  # 各方向にひとつづつ進める

        difference = abs(np.sum(np.copy(instate) - arrayclone))
        arrayclone[index[0]][index[1]] = side
        return arrayclone, difference
    def logmake(self,act):
        statesetlist, qr = self.qtable.qtableread(self.environment.state, self.side)
        self.log.append([self.turn, self.environment.actlist, act, qr, statesetlist, copy(self.environment.state)])
    def save(self, reword):  # dict[ターン数][石値合計][選択肢の数]=[[state,{行動:[試行回数,行動価値] ...}],...]
        # step[0]:ターン数、step[1]:選択肢の配列、step[2]:選択した行動、step[3]:盤面num step[4]:dict
        for t, step in enumerate(self.log):
            r = reword * GAMMA ** (len(self.log) - (t + 1))
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



