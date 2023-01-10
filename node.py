from queue import Queue

class node:
    '''
        这是node类
    '''
    id = 0                      #node对应的编号
    packetQueue = Queue()       #节点的队列
    curTime = 0
    capacity = 0
    size = 0
    bandWidth = 0               #链路带宽
    neighbor = {}               #节点相邻节点，需要给出对应的边和对应节点，以字典形式保存：key = id，value = [边类，节点类]
    def __init__(self, _id, _capacity = 100, _bandWidth = 100) -> None:
        '''
            初始化node, 需要传入相邻的节点以及对应的边,以一个字典的形式保存;还需传入相应的id
        '''
        self.id = _id
        self.capacity = _capacity
        self.bandWidth = _bandWidth
    def setNeighbor(self, node, edge):
        '''
            设置临接node
        '''
        self.neighbor[node.id] = [edge, node]
    def recv(self, packet):
        '''
            接收packet,这里如果遇到发给自己的就先不处理了,交给simulation类去处理。
        '''
        if self.size >= self.capacity:
            return            
        self.packetQueue.put(packet)
        self.size += 1

    def update(self, _curTime):
        '''
            更新时间
        '''
        self.curTime = _curTime
    '''
    def send(self, dst = 1, packetNum = 1):
        # 包发送函数:需要指定目的节点的id,以及发送包的个数,以1000个为基本单位
        pass
    '''
