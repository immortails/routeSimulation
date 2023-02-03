import networkx as nx
import numpy as np
G = nx.Graph()
nx.add_path(G, [0, 1, 2])
nx.add_path(G, [0, 10, 2])
a = nx.all_shortest_paths(G, source=0, target=2)
for p in a:
    print(p)