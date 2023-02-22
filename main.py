#coding=utf-8
from simulation import simulation
from simulation import edgeInfo
from route.route import dijstraRoute
from route.route import DQRroute
import topo
import route
import topoMat

lastTime = 100000000000     #仿真长度
stepPackets = 85            #每次随机生成包数量
nodeQueueCapacity = 10000   #节点队列容量
nodeBandWidth = 250         #节点1次可以处理多少个包
curInterval = 5000          #计算当前时刻链路状态的间隔
linkUseInterval = 100       #计算链路利用率的状态间隔
linkStateDim = 25           #链路状态的Dim
oneLife = 5001              #路由的生命周期
if __name__ == '__main__':
    #传入的mat是一个领接表，元素有两项，一项是node，一项是边
    topoMatCreator = topoMat.topoMat(nodeBandWidth)
    matTopo = topoMatCreator.getGBN()
    myTopo = topo.topo(len(matTopo), matTopo, nodeQueueCapacity, nodeBandWidth, linkStateDim)
    routeArg = {
        "oneLife" : oneLife,
    }
    myRoute = DQRroute(myTopo, routeArg)
    myRoute.setMap()
    simulationArg = {
        'lastTime': lastTime,
        'stepPackets': stepPackets,
        'curStatusInterval': curInterval,
        'linkUseInterval': linkUseInterval,
        'DQN' : True
    }
    simulator = simulation(simulationArg, myTopo, myRoute)
    simulator.simulate()
    