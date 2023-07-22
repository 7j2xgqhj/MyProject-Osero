import numpy as np
NUM=1
def softmaxchoice(vlist, actlist):
    print(actlist)
    print(vlist)
    vlist=[1/i for i in vlist]
    q = [np.exp(a / NUM) for a in vlist]
    plist = [qa / sum(q) for qa in q]
    print(plist)
    act = actlist[np.random.choice(list(range(len(actlist))), p=plist)]
    return act
print(softmaxchoice([10,2,30],[[1,2],[3.4],[9,0]]))
NUM=0.1
print(softmaxchoice([10,2,30],[[1,2],[3.4],[9,0]]))
NUM=10
print(softmaxchoice([10,2,30],[[1,2],[3.4],[9,0]]))

colors=["blue", "green", "red", "black","yellow"]
nums=[10,2,1,0.5,0.1]
for i,c in zip(nums,colors):
    print(c)
    print(i)
