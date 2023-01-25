#coding=utf-8

class packet:
    '''
        一个packet代表了1个包,一个包100B,仿真步长以ms为单位
    '''        
    def __init__(self, _org = 0, _dst = 0, _next = 0, _ttl = 64, _orgTime = 0) -> None:
        self.org = _org                 #起始地址
        self.dst = _dst                 #最终目的地
        self.next = _next               #当前下一跳目的地
        self.ttl = _ttl                 #生命周期
        self.orgTime = _orgTime         #包起始时间
    
    def delTTL(self):
        '''
            ttl每走一跳自然减少
        '''
        ttl -= 1
    
    def changeNext(self, _next):
        '''
            下一跳的方向
        '''
        self.next = _next
    
    def getOrgTime(self) -> int:
        '''
            用于获取这个包初始时间
        '''
        return self.orgTime

    def __lt__(self, other):
        return self.orgTime < other.orgTime