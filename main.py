from simulation import simulation
from simulation import edgeInfo
from route.route import dijstraRoute
import topo
import route
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
    myTopo = topo.topo(len(mat), mat)
    myRoute = dijstraRoute(myTopo)
    lastTime = 10000
    simulator = simulation(mat, myTopo, myRoute, lastTime)
    simulator.simulate()
    