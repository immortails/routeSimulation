#coding=utf-8
from simulation import simulation
from simulation import edgeInfo
from route.route import dijstraRoute
from route.route import DQRroute
import topo
import route

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
    matTest = {
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

    matGBN = {
        0 : {
            2: edgeInfo(8, nodeBandWidth),
            8: edgeInfo(7, nodeBandWidth),
        },
        1 : {
            2: edgeInfo(15, nodeBandWidth),
            3: edgeInfo(9, nodeBandWidth),
        },
        2 : {
            0: edgeInfo(8, nodeBandWidth),
            1: edgeInfo(15, nodeBandWidth),
            4: edgeInfo(20, nodeBandWidth),
        },
        3 : {
            1: edgeInfo(9, nodeBandWidth),
            4: edgeInfo(16, nodeBandWidth),
        },
        4 : {
            2: edgeInfo(20, nodeBandWidth),
            3: edgeInfo(16, nodeBandWidth),
            8: edgeInfo(6, nodeBandWidth),
            9: edgeInfo(17, nodeBandWidth),
            10: edgeInfo(9, nodeBandWidth),
        },
        5 : {
            6: edgeInfo(11, nodeBandWidth),
            8: edgeInfo(10, nodeBandWidth),
        },
        6 : {
            5: edgeInfo(11, nodeBandWidth),
            7: edgeInfo(10, nodeBandWidth),
        },
        7 : {
            6: edgeInfo(10, nodeBandWidth),
            8: edgeInfo(6, nodeBandWidth),
            10: edgeInfo(10, nodeBandWidth),
        },
        8 : {
            0: edgeInfo(7, nodeBandWidth),
            4: edgeInfo(6, nodeBandWidth),
            5: edgeInfo(10, nodeBandWidth),
            7: edgeInfo(6, nodeBandWidth),
        },
        9 : {
            4: edgeInfo(17, nodeBandWidth),
            12: edgeInfo(10, nodeBandWidth),
        },
        10 : {
            4: edgeInfo(9, nodeBandWidth),
            7: edgeInfo(10, nodeBandWidth),
            11: edgeInfo(22, nodeBandWidth),
            12: edgeInfo(10, nodeBandWidth),
        },
        11 : {
            10: edgeInfo(22, nodeBandWidth),
            13: edgeInfo(10, nodeBandWidth),
        },
        12 : {
            9: edgeInfo(10, nodeBandWidth),
            10: edgeInfo(10, nodeBandWidth),
            14: edgeInfo(4, nodeBandWidth),
            16: edgeInfo(10, nodeBandWidth),
        },
        13 : {
            11: edgeInfo(10, nodeBandWidth),
            14: edgeInfo(5, nodeBandWidth),
        },
        14 : {
            12: edgeInfo(4, nodeBandWidth),
            13: edgeInfo(5, nodeBandWidth),
            15: edgeInfo(10, nodeBandWidth),
        },
        15 : {
            14: edgeInfo(10, nodeBandWidth),
            16: edgeInfo(10, nodeBandWidth),
        },
        16 : {
            12: edgeInfo(10, nodeBandWidth),
            15: edgeInfo(10, nodeBandWidth),
        },
    }
    myTopo = topo.topo(len(matGBN), matGBN, nodeQueueCapacity, nodeBandWidth, linkStateDim)
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
    