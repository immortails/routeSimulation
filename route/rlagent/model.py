from torch import nn
import torch
import numpy as np
class FeatureNetwork(nn.Module):
    '''
        nodeList暂时废弃
    '''
    def __init__(self, modelArg) -> None:
        super().__init__()
        self.arg = modelArg
        self.link_dim = self.arg['link_state_dim']                  #加2是因为要补org和dst，后面不加2了，因为我把action也放进来了
        self.hidden_dim = 1000
        self.hidden1 = nn.Linear(self.link_dim, self.hidden_dim)
        self.hidden2 = nn.Linear(self.hidden_dim, self.hidden_dim)
        self.output = nn.Linear(self.hidden_dim, self.link_dim)
        self.sigmoid = nn.Sigmoid()
        self.gru = nn.GRU(self.link_dim, self.link_dim, 1)
        self.idx_mat = torch.from_numpy(self.arg['link_connection'].astype(np.float32))

    def forward(self, inputList):                         #inputList 是特征矩阵,   nodeList是org与dst,这块要先norm一下(nodeList废弃)
        inputList = inputList.astype(np.float32)
        linkState = torch.from_numpy(inputList)
        #linkState = torch.cat((nodeList, linkState), 1)             #先和org 和 dst 拼一下
        #message passing
        for i in range(0, self.arg['T']):
            midList = self.hidden1(linkState)
            midList = self.sigmoid(midList)
            midList = self.hidden2(midList)
            midList = self.sigmoid(midList)
            midList = self.output(midList)
            midList = self.sigmoid(midList)
            midList = torch.mm(self.idx_mat, midList)               #相邻的特征累加其实就是一个矩阵乘法，就是几个特征向量的线性变换。
            midList = torch.unsqueeze(midList, 0)
            linkState = torch.unsqueeze(linkState, 0)
            #midList.reshape(1, len(midList), len(midList[0]))
            #linkState.reshape(1, len(linkState), len(linkState[0]))
            midList = self.gru(midList, linkState)
            linkState = linkState[0]
            return linkState

class ValueNetwork(nn.Module):
    def __init__(self, modelArg) -> None:
        super().__init__()
        self.arg = modelArg
        self.FeatureModel = FeatureNetwork(modelArg)
        self.link_dim = self.arg['link_state_dim']
        self.hidden_dim = 1000
        self.hidden1 = nn.Linear(self.link_dim, self.hidden_dim)
        self.hidden2 = nn.Linear(self.hidden_dim, self.hidden_dim)
        self.output1 = nn.Linear(self.hidden_dim, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, inputList):
        #提取特征
        linkState = self.FeatureModel(inputList)
        feature = torch.sum(linkState, 0)
        #Qpi函数
        value = self.hidden1(feature)
        value = self.sigmoid(value)
        value = self.hidden2(value)
        value = self.sigmoid(value)
        value = self.output1(value)
        return value

class DuelingNetwork(nn.Module):
    '''
        写的有问题,要大改
    '''
    def __init__(self, modelArg) -> None:
        super().__init__()
        self.arg = modelArg
        self.FeatureModel = FeatureNetwork(modelArg)
        self.link_dim = self.arg['link_state_dim']
        self.hidden1 = nn.Linear(self.link_dim, self.link_dim)
        self.hidden2 = nn.Linear(self.link_dim, self.link_dim)
        self.output1 = nn.Linear(self.link_dim, 1)
        self.sigmoid = nn.Sigmoid()

        self.hidden3 = nn.Linear(self.link_dim, self.link_dim)
        self.hidden4 = nn.Linear(self.link_dim, self.link_dim)
        self.output2 = nn.Linear(self.link_dim, 1)

    def forward(self, inputList):
        #提取特征
        linkState = self.FeatureModel(inputList)
        feature = torch.sum(linkState, 1)
        #advantage函数
        advantage = self.hidden1(feature)
        advantage = self.sigmoid(advantage)
        advantage = self.hidden2(advantage)
        advantage = self.sigmoid(advantage)
        advantage = self.output1(advantage)
        #valueState函数
        valueState = self.hidden3(feature)
        valueState = self.sigmoid(valueState)
        valueState = self.hidden4(valueState)
        valueState = self.sigmoid(valueState)
        valueState = self.output2(valueState)
        #最终输出actionState函数
        res = valueState - torch.max(advantage)
        res = self.sigmoid(res) * 10
        return res