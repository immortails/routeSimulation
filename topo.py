#coding=utf-8
import edge
import node
class topo:
    nodeList = {}       #topo的所有节点
    edgeList = {}       #topo的所有边
    mat = {}            #邻接表，给出边的具体信息
    status = {}         #记录(org, dst)的链路状态
    nodeQueueCapacity = 10000       #包队列大小
    nodeBandWidth = 10              #每1ms能处理多少个包
    def __init__(self, n, _mat, _nodeQueueCapacity, _nodeBandWidth) -> None:
        '''
            n是节点个数
        '''
        self.mat = _mat
        self.nodeBandWidth = _nodeBandWidth
        self.nodeQueueCapacity = _nodeQueueCapacity
        #初始化所有node
        for i in range(0, n):
            curNode = node.node(i,self.nodeQueueCapacity, self.nodeBandWidth)
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

    def getEdge(self, node1, node2, edgeInfo = None):
        '''
            获取相应的node,如果没有就新增一个
        '''
        if (node1.id, node2.id) in self.edgeList:
            return self.edgeList[(node1.id, node2.id)]
        elif (node2.id, node1.id) in self.edgeList:
            return self.edgeList[(node2.id, node1.id)]
        else:
            self.edgeList[(node1.id, node2.id)] = edge.edge(edgeInfo.delay, edgeInfo.bandWidth, node1, node2)
            return self.edgeList[(node1.id, node2.id)]

class linkInfo:
    delayList = []
    packageNum = 0
    def __init__(self) -> None:
        self.delayList = []
    def recvOK(self, delay = 0):
        self.delayList.append(delay)
    def sendOK(self):
        self.packageNum += 1