import route.rlagent.model as model
import numpy as np
from torch import nn
import torch
import os
import random
from route.rlagent.DQNagent import DQNagent
from route.rlagent.DQNagent import exp
fileIdx = '2'
class D3QNagent(DQNagent):
    def __init__(self, _arg, _topo, _kspMap) -> None:
        self.arg = _arg                                                                             #agent 所需要的一系列参数
        self.topo = _topo                                                                           #网络拓扑
        self.kspMap = _kspMap                                                                       #预计算的ksp路径
        self.lastReward = {}                                                                        #用于计算reward
        self.expQueue = []                                                                          #经验回放队列
        self.lossData = []                                                                          #记录loss的日志
        self.lossFunc = nn.MSELoss()                                                                #损失函数
        self.QstarValueMat = {}                                                                     #用于保存上一次计算的actionState，方便训练
        self.updateTime = 0                                                                         #用于记录迭代次数
        self.rewardData = []                                                                        #用于记录reward
        self.evolution = []
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
        self.advantageValueNetwork = model.ValueNetwork(self.arg['modelArg'])
        self.stateValueNetwork = model.ValueNetwork(self.arg['modelArg'])
        self.optimizerA = torch.optim.Adam(self.advantageValueNetwork.parameters(), lr=self.arg['learnRate'])
        self.optimizerS = torch.optim.Adam(self.stateValueNetwork.parameters(), lr=self.arg['learnRate'])
        self.targetAdvantageValueNetwork = model.ValueNetwork(self.arg['modelArg'])
        self.targetStateValueNetwork = model.ValueNetwork(self.arg['modelArg'])
        self.initNetwork()


    def chooseAction(self, org, dst):
        '''
            引入Dueling Network
        '''
        state = self.topo.LinkStateMat
        n = len(self.topo.edgeList)
        idx = 0
        maxValue = -10000
        #meanAdvantageValue = 0
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
            actionValue = self.advantageValueNetwork(self.topo.nodeStateMat, state)
            #meanAdvantageValue = actionValue + meanAdvantageValue
            if actionValue > maxValue:
                maxValue = actionValue
                idx = i
        #meanAdvantageValue /= self.arg['actionSpace']
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
            self.evolution.append(self.topo.evolution[:])
            if self.updateTime % 20 == 1:
                print("update step: " + str(self.updateTime) +  " reward:" + str(curReward))
            self.addExp(self.QstarValueMat[org][dst][0], self.QstarValueMat[org][dst][1], curReward,self.topo.nodeStateMat, state, org, dst)
            for i in range(0, 2):
                expLearn = self.getExp()
                self.update(expLearn)
            self.lastReward[org][dst] = 0.8 * self.lastReward[org][dst] + 0.2 * self.topo.reward
            self.lastPackets[org][dst] = self.topo.PacketNumInterval
            #self.lastLinkUseReward[org][dst] = self.topo.linkUseReward
            self.QstarValueMat[org][dst] = (self.topo.nodeStateMat, state.copy())
            if self.updateTime % 300 == 0:
                self.savePara()
        return idx

    def update(self, expLearn):
        '''
            td算法更新参数
        '''
        #注意这里，用的是tagetNetwork来更新td target
        tdTarget = expLearn.reward + self.arg['gamma']*self.cauD3QN("Target", expLearn.nextNodeState, expLearn.nextActionState, expLearn.org, expLearn.dst)       
        preValue = self.cauD3QN("Dueling", expLearn.preNodeState, expLearn.preActionState, expLearn.org, expLearn.dst)
        tdError = abs(preValue - tdTarget)
        expLearn.tdError = tdError + 0.00001
        loss = self.lossFunc(preValue, tdTarget)
        self.optimizerS.zero_grad()
        self.optimizerA.zero_grad()
        loss.backward()
        self.optimizerS.step()
        self.optimizerA.step()
        self.lossData.append(float(loss.data))
        #target network更新参数
        if self.updateTime % 100 == 0:
            self.updateTargetPara()

    def updateTargetPara(self):
        '''
            更新target network参数
        '''
        self.targetStateValueNetwork.load_state_dict(self.stateValueNetwork.state_dict())
        self.targetAdvantageValueNetwork.load_state_dict(self.advantageValueNetwork.state_dict())

    def cauD3QN(self, networkType, nodeState, actionLinkState, org, dst):
        '''
            计算D3QN的Q值
        '''
        meanAdvantageValue = 0
        n = len(self.topo.edgeList)
        state = actionLinkState.copy()
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
            actionValue = self.advantageValueNetwork(nodeState, state)
            meanAdvantageValue = actionValue + meanAdvantageValue
        meanAdvantageValue /= self.arg['actionSpace']

        lenLink = len(state)
        for i in range(0, lenLink):
            state[i][7] = 0
            state[i][8] = 0
            state[i][9] = 0
        if networkType == "Dueling":
            stateValue = self.stateValueNetwork(nodeState, state)
            advantageValue = self.advantageValueNetwork(nodeState, actionLinkState)
            return advantageValue + stateValue - meanAdvantageValue
        else:
            stateValue = self.targetStateValueNetwork(nodeState, state)
            advantageValue = self.targetAdvantageValueNetwork(nodeState, actionLinkState)
            return advantageValue + stateValue - meanAdvantageValue  

    def initNetwork(self):
        '''
            初始化神经网络参数
        '''
        filePathNetwork = './logPara/'+fileIdx+'/DQNpara.pth'
        if os.path.exists(filePathNetwork):
            state = torch.load(filePathNetwork)
            self.advantageValueNetwork.load_state_dict(state['advantageValueNetwork'])
            self.stateValueNetwork.load_state_dict(state['stateValueNetwork'])
            self.targetAdvantageValueNetwork.load_state_dict(state['targetAdvantageValueNetwork'])
            self.targetStateValueNetwork.load_state_dict(state['targetStateValueNetwork'])
            self.optimizerS.load_state_dict(state['optimizerS'])
            self.optimizerA.load_state_dict(state['optimizerA'])
            print("Dueling parameter load ok!")
        else:
            print("no")
        filePathLoss = './logPara/' + fileIdx + '/loss.npy'
        if os.path.exists(filePathLoss):
            self.lossData = np.load(filePathLoss).tolist()
            print("loss data load ok!")
        filePathReward = './logPara/' + fileIdx + '/reward.npy'
        if os.path.exists(filePathReward):
            self.rewardData = np.load(filePathReward).tolist()
            print("reward load ok!")
        filePathEvo = './logPara/' + fileIdx + '/evolution.npy'
        if os.path.exists(filePathEvo):
            self.evolution = np.load(filePathEvo).tolist()
            print("evolution load ok!")     

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
        for params in self.optimizerA.param_groups:             
            params['lr'] = self.arg['learnRate'] * np.power(float(curLength) * sampleProbablity[idx], - self.arg['beta'])
        for params in self.optimizerS.param_groups:             
            params['lr'] = self.arg['learnRate'] * np.power(float(curLength) * sampleProbablity[idx], - self.arg['beta'])
        return self.expQueue[idx]

    def savePara(self):
        '''
            保存神经网络训练参数
        '''
        print("update time: " + str(self.updateTime) + " save data")
        state = {'advantageValueNetwork': self.advantageValueNetwork.state_dict(),  'optimizerA':self.optimizerA.state_dict(),
                    'stateValueNetwork': self.stateValueNetwork.state_dict(), 'optimizerS': self.optimizerS.state_dict(),
                        'targetAdvantageValueNetwork': self.targetAdvantageValueNetwork.state_dict(), 'targetStateValueNetwork': self.targetStateValueNetwork.state_dict()}
        torch.save(state,'./logPara/' + fileIdx + '/DQNpara.pth')
        np.save('./logPara/' + fileIdx + '/loss.npy', self.lossData)
        np.save('./logPara/'+ fileIdx + '/reward.npy', self.rewardData)
        np.save('./logPara/'+ fileIdx + '/evolution.npy',self.evolution)              

    def addExp(self,_preNodeState, _preActionState, _reward, _nextNodeState, _nextActionState, _org, _dst):
        curExp = expDueling(_preNodeState.copy(), _preActionState.copy(), _reward,_nextNodeState.copy(), _nextActionState.copy(), _org, _dst)
        sorted(self.expQueue)
        self.expQueue.append(curExp)
        if len(self.expQueue) > self.arg['expQueueLength']:
            self.expQueue.pop()

class expDueling(exp):
    def __init__(self, _preNodeState, _preActionState, _reward, _nextNodeState, _nextActionState, _org, _dst) -> None:
        super().__init__(_preNodeState, _preActionState,  _reward, _nextNodeState, _nextActionState)
        self.org = _org
        self.dst = _dst

