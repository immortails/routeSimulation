class route:
    topo = None
    routeMap = {}   #二维的字典，通过routMap[org][dst]来查下一跳
    def __init__(self, _topo = None) -> None:
        self.topo = _topo
        self.setMap()
    def setMap(self):
        '''
            用于构建路由表,不同的算法就是重写此处
        '''
        pass
    def next(self, orgID, dstID):
        '''
            根据orgID 与 dstID 来查下一跳
        '''
        return self.routeMap(orgID, dstID)