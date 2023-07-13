import tkinter as tk
import numpy as np
import envgui
import threading
import random
import time
import operator
BLANK = 0  # 石が空：0
BLACK = 1  # 石が黒：1
WHITE = -1  # 石が白：2


# 要件
# 入力:行動([座標]or[])
# 出力:最新の盤面(numpy)、行動候補([[行動候補(座標リスト)]])、勝者(試合中は[])
#先手が黒、後手が白
class Environment:
    # 初期化
    def __init__(self,size=8):
        self.size=size#8 or 6 or 4
        self.reset()

    # stateの初期化
    def stateinit(self):
        self.state = np.zeros((self.size, self.size))
        self.state[int(self.size/2-1)][int(self.size/2-1)] = WHITE
        self.state[int(self.size/2)][int(self.size/2-1)] = BLACK
        self.state[int(self.size/2-1)][int(self.size/2)] = BLACK
        self.state[int(self.size/2)][int(self.size/2)] = WHITE
    def reset(self):
        self.stateinit()
        self.side = BLACK
        self.winner = []
        self.isPassed = False
        self.turn = 0
        self.actlist = []
        self.makeactlist()
    # stateの出力
    def getstate(self):
        return np.copy(self.state)

    # 勝者の出力
    def getwinner(self):
        return np.copy(self.winner)

    def getside(self):
        return self.side

    def getturn(self):
        return self.turn

    # 手番の交代
    def turn_change(self):
        if self.side == WHITE:
            self.side = BLACK
        elif self.side == BLACK:
            self.side = WHITE
        else:
            pass

    # self.actlistを更新
    def makeactlist(self):
        actionlist = []
        statecopy = np.copy(self.state)
        for i in range(int(self.size)):
            for j in range(int(self.size)):
                if statecopy[i][j] == BLANK and self.reversestones([i, j]).size != 0:
                    actionlist.append([i, j])
        if len(actionlist) == 0: actionlist.append([])
        self.actlist = actionlist

    # 行動をする。成功したらTrue、失敗ならFalseを返す
    def action(self, act):
        if act in self.actlist:
            if len(act) == 0:
                if self.isPassed:
                    self.decidewinner()
                else:
                    self.isPassed = True
            else:
                self.state = self.reversestones(act)
                self.isPassed = False
            self.turn += 1
            self.turn_change()
            self.makeactlist()
            return True
        else:
            return False

    def decidewinner(self):
        white = np.count_nonzero(self.state == WHITE)
        black = np.count_nonzero(self.state == BLACK)
        w = max(white, black)
        if white==black:
            self.winner=BLANK
        else:
            if white == w:
                self.winner = WHITE
            elif black == w:
                self.winner = BLACK

    def reversestones(self, index):  # 引数に座標、出力は変化後の盤面orダメだったらfalse
        if len(index) != 2 or self.state[index[0]][index[1]] != BLANK: return np.zeros(0)
        arrayclone = np.copy(self.state)
        for i in range(8):
            localindex = np.array(index)
            directon = [0, 0]
            returnstonelist = []
            if i == 0:
                directon = [0, -1]
            elif i == 1:
                directon = [1, -1]
            elif i == 2:
                directon = [1, 0]
            elif i == 3:
                directon = [1, 1]
            elif i == 4:
                directon = [0, 1]
            elif i == 5:
                directon = [-1, 1]
            elif i == 6:
                directon = [-1, 0]
            elif i == 7:
                directon = [-1, -1]
            isdifferentcoloredstone = False
            localindex = np.add(localindex,directon) # 各方向にひとつづつ進める
            while np.all(localindex >= 0) and np.all(localindex < int(self.size)):
                if arrayclone[localindex[0]][localindex[1]] == BLANK: break
                if arrayclone[localindex[0]][localindex[1]] == -1*self.side:  # 異なる色の石がある
                    isdifferentcoloredstone = True
                    returnstonelist.append(np.copy(localindex))
                elif isdifferentcoloredstone:  # ↑の状態を経た後かつ同じ色の石がある ひっくり返せる
                    for num in returnstonelist:
                        arrayclone[num[0]][num[1]] = self.side
                    break
                else:  # 上以外(同じ色しかない)
                    break
                localindex += directon  # 各方向にひとつづつ進める
        if np.all(self.state == arrayclone):
            return np.zeros(0)
        else:
            arrayclone[index[0]][index[1]] = self.side
            return arrayclone


if __name__ == "__main__":
    env = Environment(4)
    gui = True
    if gui:
        def gui():
            root = tk.Tk()
            envgui.EnvGUI(env=env, master=root)
        thread1 = threading.Thread(target=gui)
        thread1.start()
    while env.getwinner().size == 0:
        t = env.getside()
        if t == WHITE:
            print("turn of WHITE")
        else:
            print("turn of BLACK")
        actlist = env.actlist
        act = False
        while not act:
            time.sleep(0.5)
            print(actlist)
            print("which one? input number")
            if env.side == WHITE:
                act = env.action(random.choice(actlist))
            else:
                act = env.action(random.choice(actlist))
    winner = env.getwinner()
    print(winner)
    if winner == WHITE:
        print("winner is WHITE")
    elif winner == BLACK:
        print("winner is  BLACK")
