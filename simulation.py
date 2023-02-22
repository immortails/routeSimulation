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
        self.sendPkgMat = np.zeros((self.n, self.n)) 
        self.linkUseInterval = self.arg['linkUseInterval']

    def simulate(self):
        '''
            仿真主流程
        '''
        for i in range(1, self.lastTime):
            self.step()
            if i % self.linkUseInterval == 0:                           #定期记录链路利用率，节点队列利用率
                self.myTopo.updateLinkNodeUse()
            if i % self.curStatusInterval == 0:                         #用于更新供模型reward的参数
                self.myTopo.updateCurStatus()
            self.update()                                               #更新所有组件
            #if i % 10000 == 0:
            #    self.evolution()
        self.evolution()                                                #评估指标

    def step(self):
        '''
            仿真每一步的工作
        '''
        #每个节点定期发送包，按双峰模型来生成,最后1s就不发了，处理在流程中的包
        if self.curTime % 1000 == 0 and self.curTime + 1000 < self.lastTime:
            self.sendPkgMat = self.samplePacketNum()
        #最后一个100s就不发了，以保证当前收到的包不会扰乱下一个时刻
        if self.curTime + 1000 < self.lastTime and self.curTime % self.curStatusInterval < self.curStatusInterval - 100:
            for i in range(0, self.n):
                for j in range(0, self.n):
                    if i == j:
                        continue
                    for k in range(0, int(self.sendPkgMat[i][j]/ 900)):
                        self.createPacket(self.myTopo.nodeList[i], self.myTopo.nodeList[j])
        #处理每一条边
        for id, curEdge in self.myTopo.edgeList.items():
            curEdge.deal()
        #处理每一个节点
        for id, curNode in self.myTopo.nodeList.items():
            self.deal(curNode)

    def deal(self, curNode):
        '''
            处理每一个node的发包,这里提到simulation的原因是要记录每个包的结果,如果这个包发给自己就收下来。
            依次处理掉每个队列的包
        '''
        while len(curNode.packageQueue) != 0:
            curPacket = curNode.packageQueue.popleft()
            if curPacket.ttl == 0:
                continue
            if curPacket.dst == curNode.id:
                #self.myTopo.status[(curPacket.org, curPacket.dst)].recvOK(self.curTime - curPacket.orgTime)
                self.myTopo.curStatus[(curPacket.org, curPacket.dst)].recvOK(self.curTime - curPacket.orgTime)
                continue
            nextID = self.myRoute.next(curNode.id, curPacket.dst)
            curQueue = curNode.neighbor[nextID][2]
            if len(curQueue) >= curNode.capacity:
                curQueue.pop()
                curNode.size -= 1
            curPacket.next = nextID            
            curQueue.append(curPacket)
            curNode.size += 1

        for nextID, info in curNode.neighbor.items():
            nextQueue = info[2]
            nextEdge = info[0]
            for i in range(0, curNode.bandWidth):
                if len(nextQueue) == 0:
                    break
                curPacket = nextQueue.popleft()
                curNode.size -= 1
                if nextEdge.full():
                    #这样处理属实是因为python中的deque没有访问元素的方式，必须要拿出来，真的离谱
                    nextQueue.appendleft(curPacket)
                    curNode.size += 1
                    break
                curPacket.ttl -= 1
                nextEdge.push(curPacket)


    
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
        #self.myTopo.status[(curNode.id, dstNode.id)].sendOK()
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
        lossRate = 0.0
        DelayAvg = 0.0
        DelayDev = 0.0
        n = 0           #n是为了避免两个节点之间无数据的情况
        a = 0.02
        b = 0.002
        c = 20
        d = 10
        e = 10
        for id1, node1 in self.myTopo.nodeList.items():
            for id2, node2 in self.myTopo.nodeList.items():
                if id1 == id2:
                    continue
                linkInfo = self.myTopo.status[(id1, id2)]
                if linkInfo.packageNum == 0:
                    continue
                n += 1
                lossRate += max(1.0 - float(len(linkInfo.delayList)) / linkInfo.packageNum, 0)
                if len(linkInfo.delayList) != 0:
                    DelayAvg += np.mean(linkInfo.delayList)
                    DelayDev += np.std(linkInfo.delayList)
        if n == 0:
            return
        linkUseFinal = np.mean(self.myTopo.linkUseRecord) 
        nodeUseFinal = np.mean(self.myTopo.nodeUseRecord)
        reward = a * float(DelayAvg) / n + b * float(DelayDev) / n + c * float(lossRate) / n
        print(" reward: "  + str(reward) + " delayAvg: " + str(DelayAvg/n) + " delayStd: " + str(DelayDev/n) 
                + " lossRate: " + str(lossRate/n) + " linkUse: " + str(np.mean(linkUseFinal)) + " nodeUse: " + str(np.mean(nodeUseFinal)))

    def samplePacketNum(self):
        '''
            采用双峰模型构建流量
        '''
        p = np.random.sample()
        c1 = 5000
        c2 = 3500
        sigma = 600
        num = 0
        if p < 0.8:
            num = np.random.normal(c1, sigma, self.n * self.n)
        else:
            num = np.random.normal(c2, sigma, self.n * self.n)
        num.resize((self.n, self.n))
        return num


class edgeInfo:
    delay = 0
    bandWidth = 0
    def __init__(self, _delay, _bandWidth) -> None:
        self.delay = _delay
        self.bandWidth = _bandWidth