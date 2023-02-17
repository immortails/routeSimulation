import route.rlagent.model as model
import numpy as np
from torch import nn
import torch
import os
import random
from DQNagent import DQNagent
from DQNagent import exp
class DoubleDQNagent(DQNagent):
    def __init__(self, _arg, _topo, _kspMap) -> None:
        super().__init__(_arg, _topo, _kspMap)
    def chooseAction(self, org, dst):
        return super().chooseAction(org, dst)
    def update(self, expLearn):
        return super().update(expLearn)