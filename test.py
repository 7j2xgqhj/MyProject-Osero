import numpy as np

def softmaxchoice(vlist, actlist):
    print(actlist)
    print(vlist)
    vlist=[1/i for i in vlist]
    q = [np.exp(a / 0.4) for a in vlist]
    plist = [qa / sum(q) for qa in q]
    print(plist)
    act = actlist[np.random.choice(list(range(len(actlist))), p=plist)]
    return act
print(softmaxchoice([10,2,30],[[1,2],[3.4],[9,0]]))