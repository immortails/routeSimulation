from torch import nn
import torch
class FeatureNetwork(nn.Module):
    def __init__(self, modelArg) -> None:
        super().__init__()
        self.arg = modelArg
        self.link_dim = self.arg['link_state_dim'] + 2             #加2是因为要补org和dst
        self.hidden1 = nn.Linear(self.link_dim, self.link_dim)
        self.hidden2 = nn.Linear(self.link_dim, self.link_dim)
        self.output = nn.Linear(self.link_dim, self.link_dim)
        self.sigmoid = nn.Sigmoid()
        self.gru = nn.GRU(self.link_dim, self.link_dim, 1)
        self.idx_mat = torch.from_numpy(self.idxMat(self.arg['link_connection']))

    def forward(self, inputList, nodeList):                         #inputList 是特征矩阵,   nodeList是org与dst,这块要先norm一下  
        linkState = torch.from_numpy(inputList)
        linkState = torch.cat((nodeList, linkState), 1)             #先和org 和 dst 拼一下
        #message passing
        for i in range(0, self.arg['T']):
            midList = self.hidden1(linkState)
            midList = self.sigmoid(midList)
            midList = self.hidden2(midList)
            midList = self.sigmoid(midList)
            midList = self.output(midList)
            midList = self.sigmoid(midList)
            midList = torch.mm(self.idx_mat, midList)               #相邻的特征累加其实就是一个矩阵乘法，就是几个特征向量的线性变换。
            midList = self.gru([midList], [linkState])
            linkState = midList[0]
            return linkState

class DuelingNetwork(nn.module):
    def __init__(self, modelArg) -> None:
        super().__init__()
        self.arg = modelArg
        self.FeatureModel = FeatureNetwork(modelArg)
        self.link_dim = self.arg['link_state_dim'] + 2
        self.hidden1 = nn.Linear(self.link_dim, self.link_dim)
        self.hidden2 = nn.Linear(self.link_dim, self.link_dim)
        self.output1 = nn.Linear(self.link_dim, self.arg['feature_num'])
        self.sigmoid = nn.Sigmoid()

        self.hidden3 = nn.Linear(self.link_dim, self.link_dim)
        self.hidden4 = nn.Linear(self.link_dim, self.link_dim)
        self.output2 = nn.Linear(self.link_dim, self.arg['feature_num'])

    def forward(self, inputList, nodeList):
        #提取特征
        linkState = self.FeatureModel(inputList, nodeList)
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
        res = valueState - torch.ones(self.arg['feature_num'], 1) * torch.max(advantage)
        res = self.sigmoid(res)
        return res
