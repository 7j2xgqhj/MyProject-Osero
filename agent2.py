from numpy import copy
from random import choice
import numpy as np
import qtable
import commonfunc as cf
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
        self.priority_action=Parameter.priority_action
        self.not_priority_action =Parameter.not_priority_action
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
        if self.isforeseeing:
            act = cf.foreseeingfunc_ver2(self.side, self.environment.state, self.environment.actlist)
        else:
            #act=cf.foreseeingfunc_ver2(self.side,self.environment.state,self.environment.actlist)
            act=cf.foreseeingfunc_ver1(self.environment.actlist)
        if self.issave:
            self.logmake(act)
        return act
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



