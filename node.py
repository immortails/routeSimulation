#coding=utf-8

from queue import Queue
from collections import deque
class node:
    '''
        这是node类
    '''             
    def __init__(self, _id, _capacity = 100, _bandWidth = 100) -> None:
        '''
            初始化node, 需要传入相邻的节点以及对应的边,以一个字典的形式保存;还需传入相应的id
            每个链路一个队列
        '''
        #Python中，成员变量一定要在init里赋值
        self.id = _id                                   #node对应的编号
        self.capacity = _capacity                       #节点容量
        self.bandWidth = 2 * _bandWidth                 #链路带宽
        self.neighbor = {}                              #节点相邻节点，需要给出对应的边和对应节点，以字典形式保存：key = id，value = [边类，节点类]
        self.packageQueue = deque()                     #暂存区
        self.curTime = 0
        self.size = 0
    def setNeighbor(self, node, edge):
        '''
            设置临接node
        '''
        self.neighbor[node.id] = [edge, node, deque()]
    def recv(self, packet):
        '''
            接收packet,首先分到相应缓冲区的队列中去,交给simulation类去处理。
            多出来的包就pop掉前面的
        '''
        self.packageQueue.append(packet)

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
