#coding=utf-8
from simulation import simulation
from simulation import edgeInfo
from route.route import dijstraRoute
import topo
import route

lastTime = 10000            #仿真长度
stepPackets = 10            #每次随机生成包数量
nodeQueueCapacity = 10000   #节点队列容量
nodeBandWidth = 10          #节点1次可以处理多少个包
curInterval = 60            #计算当前时刻链路状态的间隔

if __name__ == '__main__':
    #传入的mat是一个领接表，元素有两项，一项是node，一项是边
    mat = {
        0 : {
                1: edgeInfo(10, 10),
                3: edgeInfo(10, 10)
            },
        1 : {
                0: edgeInfo(10, 10),
                2: edgeInfo(10, 10),
                4: edgeInfo(10, 10)
            },
        2 : {
                1: edgeInfo(10, 10),
                3: edgeInfo(10, 10),
                4: edgeInfo(10, 10)
            },
        3 : {
                0: edgeInfo(10, 10),
                2: edgeInfo(10, 10),
                5: edgeInfo(10, 10),
                6: edgeInfo(10, 10)
            },
        4 : {
                1: edgeInfo(10, 10),
                2: edgeInfo(10, 10),
                5: edgeInfo(10, 10)
            },
        5 : {
                3: edgeInfo(10, 10),
                4: edgeInfo(10, 10),
                6: edgeInfo(10, 10)
            },
        6 : {
                3: edgeInfo(10, 10),
                5: edgeInfo(10, 10)
            },
    }

    myTopo = topo.topo(len(mat), mat, nodeQueueCapacity, nodeBandWidth)
    myRoute = dijstraRoute(myTopo)
    myRoute.setMap()
    simulationArg = {
        'lastTime': lastTime,
        'stepPackets': stepPackets,
        'curStatusInterval': curInterval,
    }
    simulator = simulation(simulationArg, myTopo, myRoute)
    simulator.simulate()
    