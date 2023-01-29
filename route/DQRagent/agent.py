import DQR
import numpy as np
from torch import nn
import torch
import os
class agent:
    def __init__(self, _arg, _topo, _kspMap) -> None:
        '''
            arg 参数包括 ifUpdate, modelArg, actionSpace, learnRate, expQueueLength, beta
        '''
        self.arg = _arg                                                                             #agent 所需要的一系列参数
        self.topo = _topo                                                                           #网络拓扑
        self.kspMap = _kspMap                                                                       #预计算的ksp路径
        self.lastReward = 0                                                                         #用于计算reward
        self.expQueue = []                                                                          #经验回放队列
        self.DQNnetwork = DQR.ValueNetwork(self.arg['modelArg'])                                    #神经网络
        self.optimizer = torch.optim.adam(self.DQNnetwork.parameters(), lr=self.arg['learnRate'])   #优化器
        self.lossFunc = nn.MSELoss()                                                                #损失函数
        self.QstarValueMat = {}                                                                     #用于保存上一次计算的reward，方便训练
        n = len(self.topo.nodeList)                                  
        for i in range(0, n):
            self.QstarValueMat[i] = {}
        self.initNetwork()

    def initNetwork(self):
        '''
            初始化神经网络参数
        '''
        filePath = './DQNpara.pth'
        if os.path.exists(filePath) == False:
            return
        state = torch.load(filePath)
        self.DQNnetwork.load_state_dict(state['DQNNetwork'])
        self.optimizer.load_state_dict(state['optimizer'])
    
    def chooseAction(self, org, dst):
        state = self.topo.LinkStateMat
        n = len(self.topo.edgeList)
        idx = 0
        maxValue = 0
        maxActionState = None
        for i in range(0, self.arg['actionSpace']):
            path = self.kspMap[org][dst][i]
            #clear
            for id in range(0, n):
                state[id][4] = 0
            state[org] = 1.0 / (len(path) + 1) 
            #赋值路径
            j = 2
            for id in path:
                state[id][4] = j / (len(path) + 1)
                j += 1
            #计算相应action的Qpi, 得到最大的Qpi路径
            featureValue = self.DQNnetwork(state)
            if featureValue > maxValue:
                maxValue = featureValue
                idx = i
        #重新再赋值一下最大的state
        path = self.kspMap[org][dst][idx]
        for id in range(0, n):
            state[id][4] = 0
        state[org] = 1.0 / (len(path) + 1) 
        j = 2
        for id in path:
            state[id][4] = j / (len(path) + 1)
            j += 1       
        #判断是否更新网络
        if self.arg['ifUpdate'] and self.lastReward != 0 and dst in self.QstarValueMat[org]:
            curReward =  self.lastReward - self.topo.reward             #因为绝对reward是负的，所以相对reward反着减
            self.addExp(self.QstarValueMat[org][dst], curReward, maxValue)
            expLearn = self.getExp()
            self.update(expLearn)
            self.QstarValueMat[org][dst] = maxValue
            self.lastReward = self.topo.reward
        return idx
    
    def addExp(self, _preStateAction, _reward, _nextStateAction):
        curExp = exp(_preStateAction, _reward, _nextStateAction)
        sorted(self.expQueue)
        if len(self.expQueue) > self.arg['expQueueLength']:
            self.expQueue.pop()
    
    def getExp(self):
        '''
            从经验池中按照tdloss的大小获取样本
            首先构建采样概率，然后再采样
        '''
        curLength = min(len(self.expQueue), self.arg['expQueueLength'])
        sampleProbablity = np.ones((curLength, 1))
        for i in range(0, len(sampleProbablity)):
            sampleProbablity[i] = self.expQueue[i].tdError
        sampleProbablity = sampleProbablity / sum(sampleProbablity)
        idx = np. random.sample(a = range(0, len(sampleProbablity)), p = sampleProbablity)
        #根据采样概率动态更新学习率
        for params in self.optimizer.param_groups:             
            params['lr'] = self.arg['learnRate'] * np.power(float(curLength) * sampleProbablity[idx], - self.arg['beta'])
        return self.expQueue[idx]

    def update(self, expLearn):
        '''
            td算法更新参数
        '''
        tdTarget = expLearn.reward + self.DQNnetwork(expLearn.nextateAction)
        tdError = expLearn.preQstarValue - tdTarget
        expLearn.tdError = tdError + 0.00001
        loss = self.lossFunc(expLearn.preQstarValue, tdTarget)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def savePara(self):
        '''
            保存神经网络训练参数
        '''
        state = {'DQNNetwork':self.DQNnetwork.state_dict(), 'optimizer':self.optimizer.state_dict()}
        torch.save(state,'./DQNpara.pth')

class exp:
    def __init__(self, _preQstarValue, _reward, _nextQstarValue) -> None:
        '''
            注意这里td_error实际的max不太清楚,后面训练要去修改
        '''
        self.tdError = 1
        self.preQstarValue = _preQstarValue
        self.reward = _reward
        self.nextQstarValue = _nextQstarValue
    def __rt__(self, other):
        return self.tdError > other.tdError