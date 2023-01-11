#coding=utf-8

import topo
import route.route as rt
import packet
import numpy as np
import random
class simulation:
    lastTime = 100
    myTopo = None
    myRoute = None
    n = 0
    stepPackets = 20   #每1ms一个node最多发多少包
    curTime = 0 
    def __init__(self, _topo, _route, _lastTime, _stepPackets) -> None:
        self.myTopo = _topo
        self.n = len(self.myTopo.mat)
        self.myRoute = _route
        self.lastTime = _lastTime
        self.stepPackets = _stepPackets

    def simulate(self):
        '''
            仿真主流程
        '''
        for i in range(0, self.lastTime):
            self.step()
        #仿真结束评估指标
        self.evolution()

    def step(self):
        '''
            仿真每一步的工作
        '''
        #处理每一条边
        for id, curEdge in self.myTopo.edgeList.items():
            curEdge.deal()
        #处理每一个节点
        for id, curNode in self.myTopo.nodeList.items():
            self.deal(curNode)
        #每个节点定期发送包，这个怎么处理,最后1s就不发了，处理在流程中的包
        if self.curTime + 1000 < self.lastTime:
            for id in range(0, self.n):
                packetNum = random.randint(1, self.stepPackets)
                for i in range(0, packetNum):
                    dstID = random.randint(0, self.n - 1)
                    self.createPacket(self.myTopo.nodeList[id], self.myTopo.nodeList[dstID])
        self.update()           #更新所有组件

    def deal(self, curNode):
        '''
            处理每一个node的发包,这里提到simulation的原因是要记录每个包的结果,如果这个包发给自己就收下来。
        '''
        num = 0
        while num <= curNode.bandWidth:
            if len(curNode.packetQueue) == 0:
                break
            curPacket = curNode.packetQueue.popleft()
            curNode.size -= 1
            #如果发送到目的地，收下来并记录
            if curPacket.ttl == 0:
                continue
            if curPacket.dst == curNode.id:
                if curPacket.org == 0 and curPacket.dst == 5:
                    a = 1
                self.myTopo.status[(curPacket.org, curPacket.dst)].recvOK(self.curTime - curPacket.orgTime)
            #发送给目的地
            else:
                num += 1
                nextID = self.myRoute.next(curNode.id, curPacket.dst)
                curEdge = self.myTopo.getEdge(node1 = curNode, node2 = self.myTopo.nodeList[nextID])
                if curEdge.full():
                    #这样处理属实是因为python中的deque没有访问元素的方式，必须要拿出来，真的离谱
                    curNode.packetQueue.appendleft(curPacket)
                    curNode.size += 1
                    continue
                curPacket.changeNext(nextID)
                curPacket.ttl -= 1
                curEdge.push(curPacket)

    
    def createPacket(self, curNode, dstNode):
        '''
            从curNode创建一个包发送到dstNode
        '''
        if curNode.id == dstNode.id:
            return
        nextID = self.myRoute.next(curNode.id, dstNode.id)
        curPacket = packet.packet(curNode.id, dstNode.id, nextID, 64, self.curTime)
        curEdge = self.myTopo.getEdge(node1 = curNode, node2 = self.myTopo.nodeList[nextID])
        curEdge.push(curPacket)
        self.myTopo.status[(curNode.id, dstNode.id)].sendOK()
        

    def update(self):
        self.curTime += 1
        #更新每一条边
        for id, curEdge in self.myTopo.edgeList.items():
            curEdge.update(self.curTime)
        #更新每一个节点
        for id, curNode in self.myTopo.nodeList.items():
            curNode.update(self.curTime)

    def evolution(self):
        '''
            评价拓扑指标
        '''
        for id1, node1 in self.myTopo.nodeList.items():
            for id2, node2 in self.myTopo.nodeList.items():
                if id1 == id2:
                    continue
                linkInfo = self.myTopo.status[(id1, id2)]
                lossRate = 1.0 - float(len(linkInfo.delayList)) / linkInfo.packageNum
                DelayAvg = np.mean(linkInfo.delayList)
                DelayDev = np.var(linkInfo.delayList)
                print("node" + str(id1) + " to node" + str(id2) + ": lossRate: " + str(lossRate) + ", delay avg: " + str(DelayAvg) + ", delay dev: " + str(DelayDev))


class edgeInfo:
    delay = 0
    bandWidth = 0
    def __init__(self, _delay, _bandWidth) -> None:
        self.delay = _delay
        self.bandWidth = _bandWidth