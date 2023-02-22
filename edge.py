#coding=utf-8

from queue import PriorityQueue
from collections import deque
class edge:
    '''
        描述链路
    '''               
    def __init__(self,_id, _delay, _bandWidth, _node1, _node2) -> None:
        self.id = _id
        self.delay = _delay                                         #链路时延
        self.curTime = 0                                            #当前仿真时间
        self.packetQueue = deque()                          #用于存放链路中包的队列，以时延为排序方式的优先队列，无大小限制
        self.neighborNode = {}                                      #相邻两个node
        self.curNum = 0                                             #用于记录一个step内包的队列传输了多少包，以此来控制传输带宽
        self.bandWidth = _bandWidth                                 #1ms能传多少包
        self.neighborNode[_node1.id] = _node1
        self.neighborNode[_node2.id] = _node2
    def push(self, packet):
        '''
            从node压入edge中
        '''
        if self.curNum >= self.bandWidth:
            return
        self.curNum += 1
        self.packetQueue.append([self.curTime + self.delay, packet])

    def full(self):
        return self.curNum >= self.bandWidth

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
            if len(self.packetQueue) == 0:
                break
            res = self.packetQueue.popleft()
            if res[0] > self.curTime:
                self.packetQueue.appendleft(res)
                break
            curPacket = res[1]
            nextNode = self.neighborNode[curPacket.next]
            nextNode.recv(curPacket)

