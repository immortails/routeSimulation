import networkx as nx
import numpy as np
import matplotlib.pyplot as plt


reward = np.load('./reward.npy').tolist()
loss = np.load('./loss.npy').tolist()
x = range(0, len(reward))
y = []
s = 0
for d in reward:
    s += d
    y.append(s)
x1 = range(0, len(loss))
plt.subplot(2,2,1)
plt.plot(x, reward)
plt.subplot(2,2,2)
plt.plot(x1, loss)
plt.subplot(2,2,3)
plt.plot(x, y)
plt.show()

#p = np.zeros((1, 10))
#print(p)