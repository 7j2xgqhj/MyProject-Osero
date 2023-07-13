import numpy as np
def softmax(l,t):
       q=[np.exp(a/(1/t)) for a in l]
       return [qa/sum(q) for qa in q]
print(np.sum(np.array([[1,2],[1,2]])))