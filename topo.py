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
        self.reward = 0.0                                                           #计算当前拓扑的时延，时延抖动，丢包率的reward
        self.linkUseReward = 0.0                                                    #计算当前拓扑的链路利用率reward
        self.nodeUseReward = 0.0                                                    #计算当前拓扑node利用率reward
        self.curStatus = {}                                                         #记录当前时刻的链路状态，用于算法评估环境的。
        self.lastcurStatusTime = 0                                                  #处理curStatus 接收到上一个周期的包的问题
        self.status = {}                                                            #记录(org, dst)的总的链路状态
        self.nodeList = {}                                                          #topo的所有节点
        self.edgeList = {}                                                          #topo的所有边
        self.curTime = 0                                                            #当前仿真时间
        #用于最后做统计评估的
        self.linkUseRecord = []
        self.nodeUseRecord = []
        self.evolution = []
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
        self.linkUseList = np.zeros((1, len(self.edgeList)))[0].tolist()                #链路利用率
        self.useNum = 0                                                                 #统计一个时间段内计算了多少次链路利用率
        self.LinkStateMat = np.zeros((len(self.edgeList), _linkStateDim))               #提供所有链路的特征矩阵
        self.PacketNumInterval = 0                                                      #记录这个时刻发出去的包个数  
        self.initLinkState()         
        #初始化节点状态矩阵     
        self.nodeStateMat = np.zeros((len(self.nodeList),_linkStateDim))                #记录所有节点的特征矩阵
        self.nodeUseList = np.zeros((1, len(self.nodeList)))[0].tolist()                #节点的队列利用率，次数统计直接使用linkUseNum
        self.initNodeState()
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
        self.updateLinkNodeState()
        self.cauReward()
        for id1 in range(0, self.num):
            for id2 in range(0, self.num):
                if id1 == id2:
                    continue
                #todo：这里缺一个更新指标的东西，reward没想好怎么写
                self.curStatus[(id1, id2)].clear()
        self.lastcurStatusTime = self.curTime
    
    def cauReward(self):
        #计算reward的函数，这里算出来的是绝对reward，实际使用时候应用相对的reward
        #时延，时延抖动，丢包率
        #curStatus计算时候会有一个问题，上个时刻发出去的包会在这个时刻被收下来，这个时刻的包会留到下个时刻
        DelayAvg = 0
        DelayDev = 0
        lossRate = 0
        linkUse = []
        nodeUse = []
        n = 0           #n是为了避免两个节点之间无数据的情况
        a = 0.02
        b = 0.002
        c = 20
        d = 10
        e = 10
        self.PacketNumInterval = 0                              #先清零流量记录
        for id1, node1 in self.nodeList.items():
            for id2, node2 in self.nodeList.items():
                if id1 == id2:
                    continue
                linkInfo = self.curStatus[(id1, id2)]
                self.PacketNumInterval += linkInfo.packageNum
                if linkInfo.packageNum == 0:
                    continue
                n += 1
                lossRate += max(1.0 - float(len(linkInfo.delayList)) / linkInfo.packageNum, 0)
                if len(linkInfo.delayList) != 0:
                    DelayAvg += np.mean(linkInfo.delayList)
                    DelayDev += np.std(linkInfo.delayList)
        if n == 0:
            return
        for i in range(0, len(self.LinkStateMat)):
            linkUse.append(self.LinkStateMat[i][0])
        for i in range(0, len(self.nodeStateMat)):
            nodeUse.append(self.nodeStateMat[i][0])
        self.linkUseReward = np.std(linkUse) 
        self.nodeUseReward = np.std(nodeUse)
        #self.linkUseRecord.append(self.linkUseReward)
        #self.nodeUseRecord.append(self.nodeUseReward)
        self.reward = a * float(DelayAvg) / n + b * float(DelayDev) / n + c * float(lossRate) / n + d * float(self.linkUseReward) / n + e * float(self.nodeUseReward)
        #self.reward = -d * linkUse
        self.evolution = [float(DelayAvg) / n, float(DelayDev) / n, float(lossRate) / n, np.mean(linkUse), np.mean(nodeUse)]
        print("step:" + str(self.curTime) + " packets: " + str(self.PacketNumInterval) + " reward: " 
            + str(self.reward) + " delayAvg: " + str(DelayAvg/n) + " delayStd: " + str(DelayDev/n) 
                + " lossRate: " + str(lossRate/n) + " linkUseStd: " + str(self.linkUseReward) + " NodeUseStd: " + str(self.nodeUseReward))
        print(" linkUse: " + str(np.mean(linkUse)) + " nodeUse: " + str(np.mean(nodeUse)))

    def updateLinkNodeUse(self):
        '''
            记录link与node的利用率,用于计算reward时平均
        '''
        for ids, link in self.edgeList.items():
            self.linkUseList[link.id] += float(link.curNum) / link.bandWidth 
        for ids, node in self.nodeList.items():
            self.nodeUseList[node.id] += float(node.size) / node.capacity
        self.useNum += 1     
            
    def updateLinkNodeState(self):
        '''
            更新链路利用率,节点队列利用率
        '''
        #更新linkstate的矩阵，主要是更新链路容量这个参数
        for ids, link in self.edgeList.items():
            self.LinkStateMat[link.id][0] = float(self.linkUseList[link.id]) / self.useNum
            self.LinkStateMat[link.id][1] = float(self.linkUseList[link.id]) / self.useNum
            self.linkUseList[link.id] = 0
        for id, node in self.nodeList.items():
            self.nodeStateMat[node.id][0] = float(self.nodeUseList[node.id]) / self.useNum
            self.nodeStateMat[node.id][1] = float(self.nodeUseList[node.id]) / self.useNum
            self.nodeStateMat[node.id][2] = float(self.nodeUseList[node.id]) / self.useNum
            self.nodeUseList[node.id] = 0
        self.useNum = 0

    def initLinkState(self):
        #初始化链路状态矩阵的函数
        #x1是link Capacity, x2是degree centrality, x3是link Betweenness centrality, x4是是否选取， x5是顺序, init这里只初始化x1,2,3
        n = len(self.edgeList)
        #赋值x1
        for ids, link in self.edgeList.items():
            self.LinkStateMat[link.id][0] = float(link.curNum) / link.bandWidth
            self.LinkStateMat[link.id][1] = float(link.curNum) / link.bandWidth
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
                self.LinkStateMat[id][2] = degree
                self.LinkStateMat[id][3] = degree
        #link betweenness centrality
        G1 = nx.Graph()
        for id in range(0, len(self.mat)):
            G1.add_node(id)
        for id1, nextList in self.mat.items():
            for id2, eInfo in nextList.items():
                if G1.has_edge(id1, id2) == False:
                    G1.add_weighted_edges_from([(id1, id2, eInfo.delay)])
        allBetweenness = nx.edge_betweenness_centrality(G1)
        for ids, betweenness in allBetweenness.items():
            curLink = self.getEdge(self.nodeList[ids[0]], self.nodeList[ids[1]])
            self.LinkStateMat[curLink.id][4] = betweenness
            self.LinkStateMat[curLink.id][5] = betweenness
        a = 1

    def initNodeState(self):
        '''
            初始化节点状态矩阵
            节点特征:队列占用率，度，紧密中心性，
            0, 1, 2队列占用率 3,4 度 5, 6 closeness centrality
        '''
        n = len(self.nodeList)
        #添加节点队列占用率
        for id, node in self.nodeList.items():
            self.nodeStateMat[node.id][0] = float(node.size) / (node.capacity * len(node.neighbor))
            self.nodeStateMat[node.id][1] = float(node.size) / (node.capacity * len(node.neighbor))
        #创建图，添加节点与边
        G = nx.Graph()
        for id in range(0, len(self.mat)):
            G.add_node(id)
        for id1, nextList in self.mat.items():
            for id2, eInfo in nextList.items():
                if G.has_edge(id1, id2) == False:
                    G.add_weighted_edges_from([(id1, id2, eInfo.delay)])
        #计算degree            
        allDegree = nx.degree_centrality(G)
        for id, degree in allDegree.items():
            self.nodeStateMat[id][3] = degree
            self.nodeStateMat[id][4] = degree

        #计算closeness centrality
        allCloseness = nx.closeness_centrality(G)
        for id, closeness in allCloseness.items():
            self.nodeStateMat[id][5] = closeness
            self.nodeStateMat[id][6] = closeness

    def update(self, _time):
        '''
            用于更新时间
        '''
        self.curTime = _time

class linkInfo:
    '''
        记录链路状态信息
    '''           
    def __init__(self) -> None:
        self.delayList = []             #存储有效的收包时延时间
        self.packageNum = 0             #总的发包个数
    def recvOK(self, delay = 0):
        self.delayList.append(delay)
    def sendOK(self):
        self.packageNum += 1
    def clear(self):
        self.packageNum = 0
        self.delayList = []