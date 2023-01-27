#coding=utf-8
import edge
import node
import numpy as np
import networkx as nx
class topo:                 
    def __init__(self, n, _mat, _nodeQueueCapacity, _nodeBandWidth, _linkStateDim) -> None:
        '''
            n是节点个数
        '''
        self.mat = _mat                                                             #邻接表，给出边的具体信息
        self.nodeBandWidth = _nodeBandWidth                                         #每1ms能处理多少个包
        self.nodeQueueCapacity = _nodeQueueCapacity                                 #包队列大小
        self.edgeID = 0
        self.num = n                                                                #节点个数
        self.reward = 0                                                             #计算当前拓扑的reward
        self.curStatus = {}                                                         #记录当前时刻的链路状态，用于算法评估环境的。
        self.status = {}                                                            #记录(org, dst)的总的链路状态
        self.nodeList = {}                                                          #topo的所有节点
        self.edgeList = {}                                                          #topo的所有边
        self.LinkStateMat = np.zeros((len(self.edgeList), _linkStateDim))        #提供所有链路的特征矩阵  

        #初始化所有node
        for i in range(0, n):
            curNode = node.node(i, self.nodeQueueCapacity, self.nodeBandWidth)
            self.nodeList[i] = curNode
        #初始化边以及对应连接关系,初始化链路信息
        for id1, neighborList in self.mat.items():
            for id2, edgeInfo in neighborList.items():
                node1 = self.nodeList[id1]
                node2 = self.nodeList[id2]
                curEdge = self.getEdge(node1, node2, edgeInfo)
                node1.setNeighbor(node2, curEdge)
        
        for id1 in range(0, n):
            for id2 in range(0, n):
                if id1 == id2:
                    continue
                self.status[(id1, id2)] = linkInfo()
                self.curStatus[(id1, id2)] = linkInfo()

        #初始化链路状态矩阵
        self.initLinkState()         

    def getEdge(self, node1, node2, edgeInfo = None):
        '''
            获取相应的node,如果没有就新增一个
        '''
        if (node1.id, node2.id) in self.edgeList:
            return self.edgeList[(node1.id, node2.id)]
        elif (node2.id, node1.id) in self.edgeList:
            return self.edgeList[(node2.id, node1.id)]
        else:
            self.edgeList[(node1.id, node2.id)] = edge.edge(self.edgeID, edgeInfo.delay, edgeInfo.bandWidth, node1, node2)
            self.edgeID += 1
            return self.edgeList[(node1.id, node2.id)]

    def updateCurStatus(self):
        '''
            用于定时更新拓扑状态,目前该函数主要供强化学习使用
        '''
        for id1 in range(0, self.num):
            for id2 in range(0, self.num):
                if id1 == id2:
                    continue
                #todo：这里缺一个更新指标的东西，reward没想好怎么写
                self.cauReward()
                self.updateLinkState()
                self.curStatus[(id1, id2)].clear()
    
    def cauReward(self):
        #计算reward的函数，这里算出来的是绝对reward，实际使用时候应用相对的reward
        pass     

    def updateLinkState(self):
        #更新linkstate的矩阵，主要是更新链路容量这个参数
        for ids, link in self.edgeList.items():
            self.LinkStateMat[link.id][0] = float(link.curNum) / link.bandWidth

    def initLinkState(self):
        #初始化链路状态矩阵的函数
        #x1是link Capacity, x2是degree centrality, x3是link Betweenness centrality, x4是是否选取， x5是顺序, init这里只初始化x1,2,3
        n = len(self.edgeList)
        #赋值x1
        for ids, link in self.edgeList.items():
            self.LinkStateMat[link.id][0] = float(link.curNum) / link.bandWidth
        #degree centrality
        G = nx.Graph()
        for id in range(0, n):
            G.add_node(id)
        for ids, link in self.edgeList.items():
            edgeID = link.id
            curNode1 = link.neighborNode[ids[0]]
            curNode2 = link.neighborNode[ids[1]]
            for neighborID, info in curNode1.neighbor.items():
                neighborEdge = info[0]
                if link.id == neighborEdge.id:
                    continue
                if G.has_edge(link.id, neighborEdge.id) == False:
                    G.add_weighted_edges_from([(link.id, neighborEdge.id, 1)])
            for neighborID, info in curNode2.neighbor.items():
                neighborEdge = info[0]
                if link.id == neighborEdge.id:
                    continue
                if G.has_edge(link.id, neighborEdge.id) == False:
                    G.add_weighted_edges_from([(link.id, neighborEdge.id, 1)])
            allDegree = nx.degree_centrality(G)
            for id, degree in allDegree.items():
                self.LinkStateMat[id][1] = degree
        #link betweenness centrality
        G1 = nx.Graph()
        for id in range(0, len(self.mat)):
            G1.add_node(id)
        for id1, nextList in self.mat.items():
            for id2, eInfo in nextList.items():
                if G1.has_edge(id1, id2) == False:
                    G1.add_weighted_edges_from([(id1, id2, eInfo.delay)])
        allBetweenness = nx.edge_betweenness_centrality(G)
        for ids, betweenness in allBetweenness.items():
            curLink = self.getEdge(ids[0], ids[1])
            self.LinkStateMat[curLink.id][2] = betweenness

class linkInfo:
    '''
        记录链路状态信息
    '''
    delayList = []              #存储有效的收包时延时间
    packageNum = 0              #总的发包个数
    def __init__(self) -> None:
        self.delayList = []
        self.packageNum = 0
    def recvOK(self, delay = 0):
        self.delayList.append(delay)
    def sendOK(self):
        self.packageNum += 1
    def clear(self):
        self.packageNum = 0
        self.delayList.clear()