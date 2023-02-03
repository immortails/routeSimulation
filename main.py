#coding=utf-8
from simulation import simulation
from simulation import edgeInfo
from route.route import dijstraRoute
from route.route import DQRroute
import topo
import route

lastTime = 10000            #仿真长度
stepPackets = 4             #每次随机生成包数量
nodeQueueCapacity = 200     #节点队列容量
nodeBandWidth = 10          #节点1次可以处理多少个包
curInterval = 100           #计算当前时刻链路状态的间隔
linkStateDim = 25           #链路状态的Dim
oneLife = 100               #路由的生命周期
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
            2: edgeInfo(10, 10),
            8: edgeInfo(10, 10),
        },
        1 : {
            2: edgeInfo(10, 10),
            3: edgeInfo(10, 10),
        },
        2 : {
            0: edgeInfo(10, 10),
            1: edgeInfo(10, 10),
            4: edgeInfo(10, 10),
        },
        3 : {
            1: edgeInfo(10, 10),
            4: edgeInfo(10, 10),
        },
        4 : {
            2: edgeInfo(10, 10),
            3: edgeInfo(10, 10),
            8: edgeInfo(10, 10),
            9: edgeInfo(10, 10),
            10: edgeInfo(10, 10),
        },
        5 : {
            6: edgeInfo(10, 10),
            8: edgeInfo(10, 10),
        },
        6 : {
            5: edgeInfo(10, 10),
            7: edgeInfo(10, 10),
        },
        7 : {
            6: edgeInfo(10, 10),
            8: edgeInfo(10, 10),
            10: edgeInfo(10, 10),
        },
        8 : {
            0: edgeInfo(10, 10),
            4: edgeInfo(10, 10),
            7: edgeInfo(10, 10),
        },
        9 : {
            4: edgeInfo(10, 10),
            12: edgeInfo(10, 10),
        },
        10 : {
            4: edgeInfo(10, 10),
            7: edgeInfo(10, 10),
            11: edgeInfo(10, 10),
            12: edgeInfo(10, 10),
        },
        11 : {
            10: edgeInfo(10, 10),
            13: edgeInfo(10, 10),
        },
        12 : {
            9: edgeInfo(10, 10),
            10: edgeInfo(10, 10),
            14: edgeInfo(10, 10),
            16: edgeInfo(10, 10),
        },
        13 : {
            11: edgeInfo(10, 10),
            14: edgeInfo(10, 10),
        },
        14 : {
            12: edgeInfo(10, 10),
            13: edgeInfo(10, 10),
            15: edgeInfo(10, 10),
        },
        15 : {
            14: edgeInfo(10, 10),
            16: edgeInfo(10, 10),
        },
        16 : {
            12: edgeInfo(10, 10),
            15: edgeInfo(10, 10),
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
        'DQN' : True
    }
    simulator = simulation(simulationArg, myTopo, myRoute)
    simulator.simulate()
    