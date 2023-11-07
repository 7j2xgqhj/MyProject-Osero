import numpy as np
from numpy import add
from numpy import copy
import commonfunc as cf
BLANK = 0  # 石が空：0
BLACK = 1  # 石が黒：1
WHITE = -1  # 石が白：2


# 要件
# 入力:行動([座標]or[])
# 出力:最新の盤面(numpy)、行動候補([[行動候補(座標リスト)]])、勝者(試合中は[])
# 先手が黒、後手が白
class Environment:
    # 初期化
    def __init__(self, size=8):
        self.size = int(size)  # 8 or 6 or 4
        self.stateinit()
        self.reset()

    # stateの初期化
    def stateinit(self):
        self.state = np.zeros((self.size, self.size), dtype=np.int8)
        c1, c2 = int(self.size / 2 - 1), int(self.size / 2)
        self.state[c1][c1], self.state[c2][c2] = WHITE, WHITE
        self.state[c2][c1], self.state[c1][c2] = BLACK, BLACK

    def reset(self):
        self.stateinit()
        self.side, self.winner, self.isPassed, self.turn,  self.prestate, self.preact,self.actlist,self.preactlist,self.statelist,self.prestatelist \
            = BLACK, None, False, 0, [], [],[],[],{},{}
        self.log={str(BLACK):[],str(WHITE):[]}
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
            self.preact, self.prestate,self.preactlist,self.prestatelist = act, copy(self.state),copy(self.actlist).tolist(),self.statelist
            if len(self.actlist)>1:
                self.log[str(self.side)].append([act,copy(self.state)])
            if len(act) == 0:
                if self.isPassed:
                    self.decidewinner()
                else:
                    self.isPassed = True
            else:
                self.state, self.isPassed = cf.reversestones(index=act,side=self.side,instate=self.state)[0], False
            self.turn += 1
            self.turn_change()
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
