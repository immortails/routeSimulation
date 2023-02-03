import route.rlagent.dqr as dqr
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
        self.lastReward = {}                                                                        #用于计算reward
        self.expQueue = []                                                                          #经验回放队列
        self.DQNnetwork = dqr.ValueNetwork(self.arg['modelArg'])                                    #神经网络
        self.optimizer = torch.optim.Adam(self.DQNnetwork.parameters(), lr=self.arg['learnRate'])   #优化器
        self.lossFunc = nn.MSELoss()                                                                #损失函数
        self.QstarValueMat = {}                                                                     #用于保存上一次计算的reward，方便训练
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
        maxValue = -10000
        for i in range(0, self.arg['actionSpace']):
            path = self.kspMap[org][dst][i]
            #clear
            for id in range(0, n):
                state[id][4] = 0
            #state[org] = 1.0 / (len(path) + 1) 
            #赋值路径
            j = 1
            preID = -1
            #注意这里要赋值的是边，不是点
            for id in path:
                if preID == -1:
                    preID = id
                    continue
                curLink = self.topo.getEdge(self.topo.nodeList[preID],self.topo.nodeList[id])
                state[curLink.id][4] = j / len(path)
                preID = id
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
        j = 1
        preID = -1
        for id in path:
            if preID == -1:
                preID = id
                continue
            curLink = self.topo.getEdge(self.topo.nodeList[preID],self.topo.nodeList[id])
            state[curLink.id][4] = j / len(path)
            preID = id
            j += 1   
        #判断是否更新网络
        if self.lastReward[org][dst] == 0 or dst not in self.QstarValueMat[org]:
            self.lastReward[org][dst] = self.topo.reward
            self.QstarValueMat[org][dst] = state[:]
            return idx

        if self.arg['ifUpdate']:
            curReward =  self.lastReward[org][dst] - self.topo.reward             #因为绝对reward是负的，所以相对reward反着减
            self.addExp(self.QstarValueMat[org][dst], curReward, state)
            expLearn = self.getExp()
            self.update(expLearn)
            self.lastReward[org][dst] = self.topo.reward
            self.QstarValueMat[org][dst] = state[:]
        return idx
    
    def addExp(self, _preStateAction, _reward, _nextStateAction):
        curExp = exp(_preStateAction[:], _reward, _nextStateAction[:])
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
        tdTarget = expLearn.reward + self.DQNnetwork(expLearn.nextActionState)
        preValue = self.DQNnetwork(expLearn.preActionState)
        tdError = abs(preValue - tdTarget)
        expLearn.tdError = tdError + 0.00001
        loss = self.lossFunc(preValue, tdTarget)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        print("loss : " + str(loss.data))

    def updateReward(self, curReward):
        self.lastReward = curReward

    def savePara(self):
        '''
            保存神经网络训练参数
        '''
        state = {'DQNNetwork':self.DQNnetwork.state_dict(), 'optimizer':self.optimizer.state_dict()}
        torch.save(state,'./DQNpara.pth')

class exp:
    def __init__(self, _preActionState, _reward, _nextActionState) -> None:
        '''
            注意这里td_error实际的max不太清楚,后面训练要去修改
        '''
        self.tdError = torch.tensor([10])
        self.preActionState = _preActionState
        self.reward = _reward
        self.nextActionState = _nextActionState
    def __lt__(self, other):
        return self.tdError > other.tdError