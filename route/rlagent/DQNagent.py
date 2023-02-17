import route.rlagent.model as model
import numpy as np
from torch import nn
import torch
import os
import random
class DQNagent:
    def __init__(self, _arg, _topo, _kspMap) -> None:
        '''
            arg 参数包括 ifUpdate, modelArg, actionSpace, learnRate, expQueueLength, beta, gamma
        '''
        self.arg = _arg                                                                             #agent 所需要的一系列参数
        self.topo = _topo                                                                           #网络拓扑
        self.kspMap = _kspMap                                                                       #预计算的ksp路径
        self.lastReward = {}                                                                        #用于计算reward
        self.expQueue = []                                                                          #经验回放队列
        self.lossData = []                                                                          #记录loss的日志
        self.DQNnetwork = model.ValueNetwork(self.arg['modelArg'])                                    #神经网络
        self.optimizer = torch.optim.Adam(self.DQNnetwork.parameters(), lr=self.arg['learnRate'])   #优化器
        self.lossFunc = nn.MSELoss()                                                                #损失函数
        self.QstarValueMat = {}                                                                     #用于保存上一次计算的actionState，方便训练
        self.updateTime = 0                                                                         #用于记录迭代次数
        self.rewardData = []                                                                        #用于记录reward
        self.lastPackets = np.zeros((len(self.topo.nodeList), len(self.topo.nodeList)))             #用于记录上一次的总packet
        #self.lastLinkUseReward = np.zeros((len(self.topo.nodeList), len(self.topo.nodeList)))       #用于记录上一次的linkUse
        n = len(self.topo.nodeList)                                  
        for i in range(0, n):
            self.QstarValueMat[i] = {}
            self.lastReward[i] = {}
        for i in range(0, n):
            for j in range(0, n):
                if i == j:
                    continue
                self.lastReward[i][j] = 0
        self.initNetwork()

    def initNetwork(self):
        '''
            初始化神经网络参数
        '''
        filePathNetwork = './DQNpara.pth'
        if os.path.exists(filePathNetwork):
            state = torch.load(filePathNetwork)
            self.DQNnetwork.load_state_dict(state['DQNNetwork'])
            self.optimizer.load_state_dict(state['optimizer'])
            print("DQNparameter load ok!")
        filePathLoss = './loss.npy'
        if os.path.exists(filePathLoss):
            self.lossData = np.load(filePathLoss).tolist()
            print("loss data load ok!")
        filePathReward = './reward.npy'
        if os.path.exists(filePathReward):
            self.rewardData = np.load(filePathReward).tolist()
            print("reward load ok!")

    
    def chooseAction(self, org, dst):
        state = self.topo.LinkStateMat
        n = len(self.topo.edgeList)
        idx = 0
        maxValue = -10000
        for i in range(0, self.arg['actionSpace']):
            path = self.kspMap[org][dst][i]
            #clear
            for id in range(0, n):
                state[id][6] = 0
                state[id][7] = 0
                state[id][8] = 0
            #赋值路径
            j = 1
            preID = -1
            #注意这里要赋值的是边，不是点
            for id in path:
                if preID == -1:
                    preID = id
                    continue
                curLink = self.topo.getEdge(self.topo.nodeList[preID],self.topo.nodeList[id])
                state[curLink.id][6] = j / len(path)
                state[curLink.id][7] = j / len(path)
                state[curLink.id][8] = j / len(path)
                preID = id
                j += 1
            #计算相应action的Qpi, 得到最大的Qpi路径
            featureValue = self.DQNnetwork(self.topo.nodeStateMat, state)
            if featureValue > maxValue:
                maxValue = featureValue
                idx = i
        #重新再赋值一下最大的state
        path = self.kspMap[org][dst][idx]
        for id in range(0, n):
            state[id][4] = 0
        j = 1
        preID = -1
        for id in path:
            if preID == -1:
                preID = id
                continue
            curLink = self.topo.getEdge(self.topo.nodeList[preID],self.topo.nodeList[id])
            state[curLink.id][6] = j / len(path)
            state[curLink.id][7] = j / len(path)
            state[curLink.id][8] = j / len(path)

            preID = id
            j += 1   
        #判断是否更新网络
        if self.lastReward[org][dst] == 0 or dst not in self.QstarValueMat[org]:
            self.lastReward[org][dst] = self.topo.reward
            self.lastPackets[org][dst] = self.topo.PacketNumInterval
            #self.lastLinkUseReward[org][dst] = self.topo.linkUseReward
            self.QstarValueMat[org][dst] = (self.topo.nodeStateMat, state.copy())
            return idx

        if self.arg['ifUpdate']:
            curReward =  self.cauReward(org, dst)
            self.updateTime += 1
            self.rewardData.append(float(curReward))
            if self.updateTime % 20 == 1:
                print("update step: " + str(self.updateTime) +  " reward:" + str(curReward))
            self.addExp(self.QstarValueMat[org][dst][0], self.QstarValueMat[org][dst][1], curReward,self.topo.nodeStateMat, state)
            for i in range(0, 5):
                expLearn = self.getExp()
                self.update(expLearn)
            self.lastReward[org][dst] = self.topo.reward
            self.lastPackets[org][dst] = self.topo.PacketNumInterval
            #self.lastLinkUseReward[org][dst] = self.topo.linkUseReward
            self.QstarValueMat[org][dst] = (self.topo.nodeStateMat, state.copy())
            if self.updateTime % 300 == 1:
                self.savePara()
        return idx
    
    def addExp(self,_preNodeState, _preStateAction, _reward,_nextNodeState, _nextStateAction):
        curExp = exp(_preNodeState.copy(), _preStateAction.copy(), _reward,_nextNodeState.copy(), _nextStateAction.copy())
        sorted(self.expQueue)
        self.expQueue.append(curExp)
        if len(self.expQueue) > self.arg['expQueueLength']:
            self.expQueue.pop()
    
    def getExp(self):
        '''
            从经验池中按照tdloss的大小获取样本
            首先构建采样概率，然后再采样
        '''
        curLength = min(len(self.expQueue), self.arg['expQueueLength'])
        idx = random.randint(0, curLength - 1)
        sampleProbablity = []
        for i in range(0, curLength):
            if torch.is_tensor(self.expQueue[i].tdError):
                sampleProbablity.append(float(abs(self.expQueue[i].tdError.clone().detach())))
            else:
                sampleProbablity.append(abs(self.expQueue[i].tdError))
        sampleProbablity = np.array(sampleProbablity)
        sampleProbablity = sampleProbablity / sum(sampleProbablity)
        idx = np.random.choice(a = range(0, len(sampleProbablity)), p = sampleProbablity)
        #根据采样概率动态更新学习率
        for params in self.optimizer.param_groups:             
            params['lr'] = self.arg['learnRate'] * np.power(float(curLength) * sampleProbablity[idx], - self.arg['beta'])
        return self.expQueue[idx]

    def update(self, expLearn):
        '''
            td算法更新参数
        '''
        tdTarget = expLearn.reward + self.arg['gamma']*self.DQNnetwork(expLearn.nextNodeState, expLearn.nextActionState)
        preValue = self.DQNnetwork(expLearn.nextNodeState, expLearn.nextActionState)
        tdError = abs(preValue - tdTarget)
        expLearn.tdError = tdError + 0.00001
        loss = self.lossFunc(preValue, tdTarget)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        self.lossData.append(float(loss.data))

    def cauReward(self, org, dst):
        '''
            用流量大小去平衡奖励
        '''
        r1 = 4               
        #r2 = 10
        a = 0
        if self.topo.reward > 0:
            a = self.lastReward[org][dst] / self.topo.reward
        else:
            a = self.topo.reward / self.lastReward[org][dst]
        #b = float(self.topo.linkUseReward) / self.lastLinkUseReward[org][dst]
        c = float(self.topo.PacketNumInterval) / float(self.lastPackets[org][dst])
        #d = 0.3 * (c - 1) + 1
        res = r1 * (a * c - 1)
        return res

    def updateReward(self, curReward):
        self.lastReward = curReward

    def savePara(self):
        '''
            保存神经网络训练参数
        '''
        print("update time: " + str(self.updateTime) + " save data")
        state = {'DQNNetwork':self.DQNnetwork.state_dict(), 'optimizer':self.optimizer.state_dict()}
        torch.save(state,'./DQNpara.pth')
        np.save('./loss.npy', self.lossData)
        np.save('./reward.npy', self.rewardData)

class exp:
    def __init__(self,_preNodeState, _preActionState, _reward,_nextNodeState, _nextActionState) -> None:
        '''
            注意这里td_error实际的max不太清楚,后面训练要去修改
        '''
        self.tdError = torch.tensor([100])
        self.preActionState = _preActionState
        self.preNodeState = _preNodeState
        self.reward = _reward
        self.nextActionState = _nextActionState
        self.nextNodeState = _nextNodeState
    def __lt__(self, other):
        return self.tdError > other.tdError