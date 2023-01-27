import DQR
import numpy as np
class agent:
    def __init__(self, _arg, _topo, _kspMap) -> None:
        '''
            arg 参数包括 ifUpdate,modelArg, actionSpace
        '''
        self.arg = _arg
        self.topo = _topo
        self.kspMap = _kspMap
        self.lastReward = 0
        self.expQueue = []
        self.learnRate = 0.001
        self.DQNnetwork = DQR.ValueNetwork(self.arg['modelArg'])
        self.stateActionMat = {}
        n = len(self.topo.nodeList)
        for i in range(0, n):
            self.stateActionMat[i] = {}
        self.initNetwork()

    def initNetwork(self):
        '''
            初始化神经网络参数
        '''
        pass
    
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
                maxActionState = state[:]
        #判断是否更新网络
        if self.arg['ifUpdate'] and self.lastReward != 0 and dst in self.stateActionMat[org]:
            curReward = self.topo.reward - self.lastReward
            self.addExp(self.stateActionMat[org][dst], curReward, maxActionState)
            expLearn = self.getExp()
            self.update(expLearn)
            self.stateActionMat[org][dst] = maxActionState
        return idx
    
    def addExp(self, _preStateAction, _reward, _nextStateAction):
        curExp = exp(_preStateAction, _reward, _nextStateAction)
        sorted(self.expQueue)
        if len(self.expQueue) > self.arg['expQueueLength']:
            self.expQueue.pop()
    
    def getExp(self):
        '''
            构建采样概率
        '''
        sampleProbablity = np.ones((self.arg['expQueueLength'], 1))
        for i in range(0, len(sampleProbablity)):
            sampleProbablity[i] = self.expQueue[i].tdError
        sampleProbablity = sampleProbablity / sum(sampleProbablity)
        idx = np. random.sample(a = range(0, len(sampleProbablity)), p = sampleProbablity)
        return sampleProbablity[idx], self.expQueue[idx]

    def update(self, expLearn):
        pass

class exp:
    def __init__(self, _preStateAction, _reward, _nextStateAction) -> None:
        '''
            注意这里td_error实际的max不太清楚,后面训练要去修改
        '''
        self.tdError = 1
        self.preStateAction = _preStateAction
        self.reward = _reward
        self.nextStateAction = _nextStateAction
    def __rt__(self, other):
        return self.tdError > other.tdError