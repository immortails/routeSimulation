#coding=utf-8
import networkx as nx
import numpy as np
from DQRagent.agent import agent
import random
class route:
    topo = None                     
    def __init__(self, _topo = None, _arg = None) -> None:
        self.topo = _topo
        self.arg = _arg
        self.routeMap = {}   #二维的字典，通过routMap[org][dst]来查下一跳
        self.routeLife = {}  #二维的字典，用于确定路由的生命周期  
        self.curTime = 0     #当前仿真时刻，用于判断路由是否过期
        self.oneLife = self.arg['oneLife']   #单条路由生命周期
        for i in range(0, len(self.topo.mat)):
            self.routeMap[i] = {}
            self.routeLife[i] = {}


    def setMap(self):
        '''
            用于构建路由表,传统的算法就是重写此处
        '''
        pass

    def next(self, orgID, dstID):
        '''
            根据orgID 与 dstID 来查下一跳
        '''
        return self.routeMap[orgID][dstID]

    def update(self, _time):
        '''
            用于更新时间，这个时间主要用于判断路由过期时间
        '''
        self.curTime = _time

class dijstraRoute(route):
    '''
        用最短路径生成的路由表
    '''
    def __init__(self, _topo=None, _arg = None) -> None:
        super().__init__(_topo, _arg)

    def setMap(self):
        #构建路由算法使用的networkx
        G = nx.Graph()
        mat = self.topo.mat
        for id in range(0, len(mat)):
            self.G.add_node(id)
        for id1, nextList in mat.items():
            for id2, eInfo in nextList.items():
                if G.has_edge(id1, id2) == False:
                    G.add_weighted_edges_from([(id1, id2, eInfo.delay)])

        n = len(self.topo.mat)
        path = dict(nx.all_pairs_dijkstra_path(G))
        for id1 in range(0, n):
            for id2 in range(0, n):
                if id1 == id2:
                    continue
                self.routeMap[id1][id2] = path[id1][id2][1]
    
class DQRroute(route):
    '''
        基于强化学习的路由策略
    '''
    def __init__(self, _topo=None, _arg = None) -> None:
        super().__init__(_topo, _arg)
        self.actionSpace = 4              #action space的空间大小
        self.modelArg = {
            'T' : 20,
            'link_state_dim': 25,
            'node_num': len(self.topo.nodeList),
            'edge_num': len(self.topo.edgeList),
            'link_connection': self.createLinkConn(self.topo.edgeList),
            'feature_num': 4,
            'beta' : 0.5,
        }
        self.agentArg = {
            'modelArg' : self.modelArg,
            'ifUpdate' : True,
            'actionSpace' : self.actionSpace,
            'learnRate' : 0.001,
            'expQueueLength': 100,
        }
        #初始化ksp查询的字典
        self.kspMap = {}
        n = len(self.topo.mat)
        for i in range(0, n):
            self.kspMap[i] = {}
        for id1 in range(0, n):
            for id2 in range(0, n):
                self.kspMap[id1][id2] = []      
        self.agent = agent(self.agentArg, self.topo, self.kspMap)   

    def createLinkConn(self, edgeList):
        '''
            创建mpnn按INDEX乘所需的矩阵
        '''
        n = len(edgeList)
        linkMat = np.zeros((n, n))
        for ids, curEdge in edgeList.items():
            curNode1 = curEdge.neighborNode[ids[0]]
            curNode2 = curEdge.neighborNode[ids[1]]
            for neighborID, info in curNode1.neighbor.items():
                neighborEdge = info[0]
                if curEdge.id == neighborEdge.id:
                    continue
                linkMat[curEdge.id][neighborEdge.id] = 1
            for neighborID, info in curNode2.neighbor.items():
                neighborEdge = info[0]
                if curEdge.id == neighborEdge.id:
                    continue
                linkMat[curEdge.id][neighborEdge.id] = 1     

    def setMap(self):
        '''
            这里用于计算所有节点的ksp吧
        '''
        n = len(self.topo.mat)
        for id1 in range(0, n):
            for id2 in range(0, n):
                kPaths = nx.all_shortest_paths(self.G, id1, id2)
                cnt = 0
                for path in kPaths:
                    if cnt > self.actionSpace:
                        break
                    self.kspMap[id1][id2].append(path)
                    cnt += 1

    def next(self, orgID, dstID):
        #路由存在且没有过期
        if dstID in self.routeMap[orgID] and self.curTime <= self.routeLife[orgID][dstID]:
            return self.routeMap[orgID][dstID]
        #路由过期
        n = len(self.kspMap[orgID][dstID])
        action = random.randint(0, n - 1)
        if n == self.actionSpace:
            action = self.agent.chooseAction(self.topo, orgID, dstID)
        path = self.kspMap[orgID][dstID][action]
        preID = -1
        for nextID in path[: -1]:
            if preID == -1:
                continue
            self.routeMap[preID][dstID] = nextID
            preID = nextID
        self.routeLife[orgID][dstID] = self.curTime + self.oneLife + random.randint(0, 10)
        return self.routeMap[orgID][dstID] 
        




            
