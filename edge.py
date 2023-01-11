#coding=utf-8

from queue import PriorityQueue
class edge:
    '''
        描述链路
    '''
    curTime = 0         #当前仿真时间
    delay = 0           #链路时延
    bandWidth = 0        #1ms能传多少包
    packetQueue = None   #用于存放链路中包的队列，以时延为排序方式的优先队列，无大小限制
    neighborNode = None       #相邻两个node
    curNum = 0
    def __init__(self, _delay, _bandWidth, _node1, _node2) -> None:
        self.delay = _delay
        self.curTime = 0
        self.packetQueue = PriorityQueue()
        self.neighborNode = {}
        self.curNum = 0
        self.bandWidth = _bandWidth
        self.neighborNode[_node1.id] = _node1
        self.neighborNode[_node2.id] = _node2
    def push(self, packet):
        '''
            从node压入edge中
        '''
        if self.curNum > self.bandWidth:
            return
        self.curNum += 1
        self.packetQueue.put([self.curTime + self.delay, packet])

    def full(self):
        return self.curNum > self.bandWidth

    def update(self, _curTime):
        '''
            更新仿真时间。
        '''
        self.curTime = _curTime
        self.curNum = 0

    def deal(self):
        '''
            从edge发送至对应的node
        '''
        for i in range(self.bandWidth):
            if self.packetQueue.empty():
                break
            res = self.packetQueue.get()
            if res[0] > self.curTime:
                self.packetQueue.put(res)
                break
            curPacket = res[1]
            nextNode = self.neighborNode[curPacket.next]
            nextNode.recv(curPacket)

