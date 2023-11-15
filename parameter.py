import os
import numpy as np


class ConstantMeta(type):
    """定数を管理するクラスのためのメタクラス。
    クラス変数の上書きや新たなクラス変数の追加をできないようにする。
    """

    # クラスが初期化されたどうかを表す変数
    _initialized = False

    def __setattr__(cls, name, value):
        if cls._initialized:
            if name in cls.__dict__:
                raise ValueError(f"{name} is a read-only property")
            else:
                raise AttributeError("Cannot add new attribute to Constants class")
        super().__setattr__(name, value)

    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls._initialized = True


class Parameter(metaclass=ConstantMeta):
    # 変更しないもの
    BLANK = 0  # 石が空：0
    BLACK = 1  # 石が黒：1
    WHITE = -1  # 石が白：2
    # たまに変更するもの
    GAMMA = 0.95  # 割引率
    EPSILON = 0.9
    TEMPERATURE = 0.01  # 温度定数初期値
    WINREWORD = 1
    LOSEREWORD = -1 * WINREWORD
    DRAWREWORD = 0.01
    VALUERATE = 0.5
    # よく変更するもの
    SIZE = 8
    PATH = "E:/qtables/" + "table" + str(SIZE) + "/"

    # よく変更するものの影響をうけるもの
    CPATH = os.path.abspath("..\\..\\qcash") + "/table" + str(SIZE) + "/"
    RAYER = int((SIZE * SIZE - 1) / 12)
    priority_action = [[0, 0], [0, SIZE - 1], [SIZE - 1, 0], [SIZE - 1, SIZE - 1]]
    not_priority_action = [[1, 0], [1, 0], [1, 1],
                           [0, SIZE - 2], [1, SIZE - 1], [1, SIZE - 2],
                           [SIZE - 2, 0], [SIZE - 1, 1], [SIZE - 2, 1],
                           [SIZE - 2, SIZE - 1], [SIZE - 1, SIZE - 2],
                           [SIZE - 2, SIZE - 2]]
    # 長いやつ
    patternmatch = [np.array([[1, 1, 1, 1, 1, 1, 1, 1],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0]]),
                    np.array([[0, 0, 0, 0, 0, 0, 0, 0],
                              [1, 1, 1, 1, 1, 1, 1, 1],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0]]),
                    np.array([[0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [1, 1, 1, 1, 1, 1, 1, 1],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0]]),
                    np.array([[1, 0, 0, 0, 0, 0, 0, 0],
                              [0, 1, 0, 0, 0, 0, 0, 0],
                              [0, 0, 1, 0, 0, 0, 0, 0],
                              [0, 0, 0, 1, 0, 0, 0, 0],
                              [0, 0, 0, 0, 1, 0, 0, 0],
                              [0, 0, 0, 0, 0, 1, 0, 0],
                              [0, 0, 0, 0, 0, 0, 1, 0],
                              [0, 0, 0, 0, 0, 0, 0, 1]]),
                    np.array([[1, 1, 1, 0, 0, 0, 0, 0],
                              [1, 1, 1, 0, 0, 0, 0, 0],
                              [1, 1, 1, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0]])
                    ]
