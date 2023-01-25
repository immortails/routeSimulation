import networkx as nx
G = nx.Graph()
G.add_edges_from([[0, 1], [0, 2], [1, 2], [2,3], [3,4], [4,5], [3,5]])
a = nx.closeness_centrality(G)
print(a)
        #赋值x2
