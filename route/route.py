import networkx as nx
class route:
    topo = None
    routeMap = {}   #二维的字典，通过routMap[org][dst]来查下一跳
    def __init__(self, _topo = None) -> None:
        self.topo = _topo
        for i in range(0, len(self.topo.mat)):
            self.routeMap[i] = {}

    def setMap(self):
        '''
            用于构建路由表,不同的算法就是重写此处
        '''
        pass

    def next(self, orgID, dstID):
        '''
            根据orgID 与 dstID 来查下一跳
        '''
        return self.routeMap[orgID][dstID]

class dijstraRoute(route):
    '''
        用最短路径生成的路由表
    '''
    def __init__(self, _topo=None) -> None:
        super().__init__(_topo)
    def setMap(self):
        G = nx.Graph()
        mat = self.topo.mat
        for id in range(0, len(mat)):
            G.add_node(id)
        for id1, nextList in mat.items():
            for id2, eInfo in nextList.items():
                if G.has_edge(id1, id2) == False:
                    G.add_weighted_edges_from([(id1, id2, eInfo.delay)])
        path = dict(nx.all_pairs_dijkstra_path(G))
        for id1 in range(0, len(mat)):
            for id2 in range(0, len(mat)):
                if id1 == id2:
                    continue
                self.routeMap[id1][id2] = path[id1][id2][1]
                
