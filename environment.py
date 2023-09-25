
import numpy as np
from numpy import add
from numpy import copy
from copy import deepcopy

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
        self.side, self.winner, self.isPassed, self.turn, self.actlist, self.prestate, self.preact \
            = BLACK, None, False, 0, [], [], []
        self.makeactlist()

    def turn_change(self):
        self.side *= -1

    # self.actlistを更新
    def makeactlist(self):
        actionlist, statecopy = [], copy(self.state)
        [actionlist.append([i, j]) for i in range(self.size) for j in range(self.size) if
         statecopy[i][j] == BLANK and self.reversestones([i, j]).size != 0]
        if len(actionlist) == 0:
            actionlist.append([])
        self.actlist = actionlist

    # 行動をする。成功したらTrue、失敗ならFalseを返す
    def action(self, act):
        if act in self.actlist:
            self.preact, self.prestate = act, copy(self.state)
            if len(act) == 0:
                if self.isPassed:
                    self.decidewinner()
                else:
                    self.isPassed = True
            else:
                self.state, self.isPassed = self.reversestones(act), False
            self.turn += 1
            self.turn_change(), self.makeactlist()
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

    def reversestones(self, index):  # 引数に座標、出力は変化後の盤面orダメだったらfalse
        arrayclone = copy(self.state)  # 参照渡し対策　必須
        for i in [[0, -1], [1, -1], [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1]]:
            localindex, directon, returnstonelist, isdifferentcoloredstone = np.array(index,
                                                                                      dtype=np.int8), i, [], False
            localindex = add(localindex, directon)  # 各方向にひとつづつ進める
            while np.all(localindex >= 0) and np.all(localindex < self.size):
                if arrayclone[localindex[0]][localindex[1]] == BLANK:
                    break
                elif arrayclone[localindex[0]][localindex[1]] == -1 * self.side:  # 異なる色の石がある
                    isdifferentcoloredstone = True
                    returnstonelist.append(copy(localindex))
                elif isdifferentcoloredstone:  # ↑の状態を経た後かつ同じ色の石がある ひっくり返せる

                    for num in returnstonelist:
                        arrayclone[num[0]][num[1]] = self.side
                    break
                else:  # 上以外(同じ色しかない)
                    break
                localindex = add(localindex, directon)  # 各方向にひとつづつ進める
        if np.all(self.state == arrayclone):
            return np.zeros(0, dtype=np.int8)
        else:
            arrayclone[index[0]][index[1]] = self.side
            return arrayclone
