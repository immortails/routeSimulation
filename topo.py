import edge
import node
class topo:
    nodeList = {}       #topo的所有节点
    edgeList = {}       #topo的所有边
    mat = {}            #邻接表，给出边的具体信息
    status = {}         #记录(org, dst)的链路状态
    def __init__(self, n, _mat) -> None:
        '''
            n是节点个数
        '''
        self.mat = _mat
        #初始化所有node
        for i in range(0, n):
            self.nodeList[i] = node.node(i, 100, 10)
        #初始化边以及对应连接关系,初始化链路信息
        for id1, neighborList in self.mat.items():
            for id2, edgeInfo in neighborList.items():
                node1 = self.nodeList[id1]
                node2 = self.nodeList[id2]
                curEdge = self.getEdge(node1, node2)
                node1.setNeighbor(node2, curEdge, edgeInfo)
                self.status[(node1.id, node2.id)] = linkInfo()

    def getEdge(self, node1, node2, edgeInfo = None):
        '''
            获取相应的node,如果没有就新增一个
        '''
        if self.edgeList.has_key((node1.id, node2.id)):
            return self.edgeList[(node1.id, node2.id)]
        elif self.edgeList.has_key((node2.id, node1.id)):
            return self.edgeList[(node1.id, node2.id)]
        else:
            self.edgeList[(node1.id, node2.id)] = edge.edge(edgeInfo.delay, edgeInfo.bandWidth, node1, node2)
            return self.edgeList[(node1.id, node2.id)]

class linkInfo:
    delayList = []
    packageNum = 0
    def __init__(self) -> None:
        pass
    def recvOK(self, delay = 0):
        self.delayList.append(delay)
    def sendOK(self):
        self.packageNum += 1