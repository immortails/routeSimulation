#coding=utf-8

import topo
import route.route as rt
import packet
import numpy as np
import random
class simulation:
    def __init__(self, _arg, _topo, _route) -> None:
        self.arg = _arg
        self.myTopo = _topo
        self.myRoute = _route
        self.n = len(self.myTopo.mat)                                   #节点个数
        self.lastTime = self.arg['lastTime']                            #仿真结束时间
        self.stepPackets = self.arg['stepPackets']                      #每1ms一个node发多少包
        self.curStatusInterval = self.arg['curStatusInterval']          #每隔多久重置一下当前时刻的链路状态
        self.curTime = 0                                                #当前时间，计时使用 

    def simulate(self):
        '''
            仿真主流程
        '''
        for i in range(1, self.lastTime):
            self.step()
            if i % self.curStatusInterval == 0:                         #用于更新供模型reward的参数
                self.myTopo.updateCurStatus()
                #self.myRoute.agent.updateReward(self.myTopo.reward)
            if self.arg['DQN'] and i % 1000 == 0:                       #保存模型参数
                self.myRoute.agent.savePara()
                print("cur step:" + str(i) + " cur reward: " + str(self.myTopo.reward))
        self.evolution()                                                #评估指标

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
                packetNum = random.randint(0, self.stepPackets)
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
                self.myTopo.status[(curPacket.org, curPacket.dst)].recvOK(self.curTime - curPacket.orgTime)
                self.myTopo.curStatus[(curPacket.org, curPacket.dst)].recvOK(self.curTime - curPacket.orgTime)
                continue
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
        self.myTopo.curStatus[(curNode.id, dstNode.id)].sendOK()        

    def update(self):
        '''
            用于更新仿真时间
        '''
        self.curTime += 1
        self.myRoute.update(self.curTime)       #更新路由
        self.myTopo.update(self.curTime)
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
        print("当前仿真步长" + str(self.curTime))
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