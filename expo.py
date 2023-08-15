import environment
import numpy as np

ENV=environment.Environment(size=4,iskeeplog=True)
SOURCE=[]
def stateTonum(state):
    state+=1
    strstate = ""
    for y in state:
        for x in y:
            strstate += str(int(x))
    return int(strstate)
def expore(actlist):
    print(actlist)
    for act in actlist:
        if len(actlist) > 1:
            SOURCE.append([ENV.getstate(),act[0],act[1]])
        if ENV.getwinner().size == 0:
            print(act)
            ENV.action(act)
            expore(ENV.getactlist())
        ENV.backlog()
expore(ENV.getactlist())
print(SOURCE)


