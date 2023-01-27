import networkx as nx
import numpy as np
a = np.array([1.0, 2.0, 3.0])
b = a / sum(a)
c = np.random.choice(a = a, p = b)
print(c)