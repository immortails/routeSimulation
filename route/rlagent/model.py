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
        self.hiddenLink1 = nn.Linear(self.link_dim, self.hidden_dim)
        self.hiddenLink2 = nn.Linear(self.hidden_dim, self.hidden_dim)
        self.outputLink = nn.Linear(self.hidden_dim, self.link_dim)

        self.hiddenNode1 = nn.Linear(self.link_dim, self.hidden_dim)
        self.hiddenNode2 = nn.Linear(self.hidden_dim, self.hidden_dim)
        self.outputNode = nn.Linear(self.hidden_dim, self.link_dim)

        self.sigmoid = nn.Sigmoid()
        self.gruNode = nn.GRU(self.link_dim, self.link_dim, 1)
        self.gruLink = nn.GRU(self.link_dim, self.link_dim, 1)
        self.linkIdxMat = torch.from_numpy(self.arg['link_connection'].astype(np.float32))
        self.nodeIdxMat = torch.from_numpy(self.arg['node_connection'].astype(np.float32))

    def forward(self,inputNodeList, inputLinkList):                         #inputList 是特征矩阵,   nodeList是org与dst,这块要先norm一下(nodeList废弃)
        inputNodeList = inputNodeList.astype(np.float32)
        inputLinkList = inputLinkList.astype(np.float32)
        linkState = torch.from_numpy(inputLinkList)
        nodeState = torch.from_numpy(inputNodeList)
        #linkState = torch.cat((nodeList, linkState), 1)             #先和org 和 dst 拼一下
        #message passing
        for i in range(0, self.arg['T']):
            midList = self.hiddenLink1(linkState)
            midList = self.sigmoid(midList)
            midList = self.hiddenLink2(midList)
            midList = self.sigmoid(midList)
            midList = self.outputLink(midList)
            midList = self.sigmoid(midList)

            #相邻的特征累加其实就是一个矩阵乘法，就是几个特征向量的线性变换。
            #先将边的特征汇聚到节点上
            midNodeFromList = torch.mm(self.nodeIdxMat, midList)
            midNodeFromList = torch.unsqueeze(midNodeFromList, 0)
            nodeState = torch.unsqueeze(nodeState, 0)
            midNodeFromList = self.gruNode(midNodeFromList, nodeState)
            nodeState = nodeState[0]
            #再将节点的特征汇聚到边上
            midNode = self.hiddenNode1(nodeState)
            midNode = self.sigmoid(midNode)
            midNode = self.hiddenNode2(midNode)
            midNode = self.sigmoid(midNode)
            midNode = self.outputNode(midNode)
            midNode = self.sigmoid(midNode)
            midListFromNode = torch.mm(self.linkIdxMat, midNode)               
            midListFromNode = torch.unsqueeze(midListFromNode, 0)
            linkState = torch.unsqueeze(linkState, 0)
            #midList.reshape(1, len(midList), len(midList[0]))
            #linkState.reshape(1, len(linkState), len(linkState[0]))
            midListFromNode = self.gruLink(midListFromNode, linkState)
            linkState = linkState[0]
            return nodeState, linkState

class ValueNetwork(nn.Module):
    def __init__(self, modelArg) -> None:
        super().__init__()
        self.arg = modelArg
        self.FeatureModel = FeatureNetwork(modelArg)
        self.link_dim = self.arg['link_state_dim']
        self.hidden_dim = 1000
        self.hidden1 = nn.Linear(2 * self.link_dim, self.hidden_dim)
        self.hidden2 = nn.Linear(self.hidden_dim, self.hidden_dim)
        self.output = nn.Linear(self.hidden_dim, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self,inputNodeList, inputLinkList):
        #提取特征
        nodeState, linkState = self.FeatureModel(inputNodeList, inputLinkList)
        featureNode = torch.sum(nodeState, 0)
        featureLink = torch.sum(linkState, 0)
        feature = torch.cat((featureNode, featureLink), 0)
        #Qpi函数
        value = self.hidden1(feature)
        value = self.sigmoid(value)
        value = self.hidden2(value)
        value = self.sigmoid(value)
        value = self.output(value)
        return 10 * value
