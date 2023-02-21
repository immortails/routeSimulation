import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

pathIdx = "1"
reward = np.load('./logPara/' + pathIdx + '/reward.npy').tolist()
loss = np.load('./logPara/' + pathIdx + '/loss.npy').tolist()

y = []
s = 0.0
num = 1
for d in reward:
    s += d
    if num % 500 == 0:
        y.append(s)
        s = 0.0
    num += 1
s = 0.0
ySum = []
for d in reward:
    s += d
    ySum.append(s)

plt.subplot(2,2,1)
plt.plot(range(0, len(reward)), reward)
plt.subplot(2,2,2)
plt.plot(range(0, len(loss)), loss)
plt.subplot(2,2,3)
plt.plot(range(0, len(y)), y)
plt.subplot(2,2,4)
plt.plot(range(0, len(ySum)), ySum)
plt.show()

a = 0.02
b = 0.002
c = 20
d = 10
e = 10

evolution = np.load('./logPara/' + pathIdx + '/evolution.npy').tolist()
delay = []
delaystd = []
loss = []
evo = []
for d in evolution[0:len(evolution):100]:
    delay.append(d[0])
    delaystd.append(d[1])
    loss.append(d[2])
    evo.append( - a * d[0] - b * d[1] - c * d[2])
plt.subplot(2, 2, 1)
plt.plot(range(0, len(delay)), delay)
plt.subplot(2, 2, 2)
plt.plot(range(0, len(delaystd)), delaystd)
plt.subplot(2, 2, 3)
plt.plot(range(0, len(loss)), loss)
plt.subplot(2, 2, 4)
plt.plot(range(0, len(evo)), evo)
plt.show()


#p = np.zeros((1, 10))
#print(p)