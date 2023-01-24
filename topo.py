#coding=utf-8
import edge
import node
class topo:
    nodeList = {}       #topo的所有节点
    edgeList = {}       #topo的所有边
    mat = {}            #邻接表，给出边的具体信息
    status = {}         #记录(org, dst)的总的链路状态
    curStatus = {}      #记录当前时刻的链路状态，用于算法评估环境的。
    nodeQueueCapacity = 10000       #包队列大小
    nodeBandWidth = 10              #每1ms能处理多少个包
    num = 0                         #节点个数
    reward = 0                   #计算当前拓扑的reward
    def __init__(self, n, _mat, _nodeQueueCapacity, _nodeBandWidth) -> None:
        '''
            n是节点个数
        '''
        self.mat = _mat
        self.nodeBandWidth = _nodeBandWidth
        self.nodeQueueCapacity = _nodeQueueCapacity
        self.edgeID = 0
        self.num = n  
        self.reward = 0 
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
        for id1 in range(0, self.num):
            for id2 in range(0, self.num):
                if id1 == id2:
                    continue
                #todo：这里缺一个更新指标的东西，reward没想好怎么写
                self.cauReward()
                self.curStatus[(id1, id2)].clear()
    
    def cauReward(self):
        #计算reward的函数，这里算出来的是绝对reward，实际使用时候应用相对的reward
        pass     

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